#!/usr/bin/env python3
"""Offline calculation only; never calls an account API or submits changes."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected non-empty text")
    return value.strip()


def number(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label}: boolean is not a number")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{label}: expected a finite non-negative number") from exc
    if not result.is_finite() or result < 0 or result > Decimal("1e15"):
        raise ValueError(f"{label}: expected a finite number in [0, 1e15]")
    return result


def integer(value, label, minimum=0):
    if type(value) is not int or value < minimum or value > 1000000000000000:
        raise ValueError(f"{label}: expected integer >= {minimum}")
    return value


def obj(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected object")
    return value


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite JSON constant: {value}")


def ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return (Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.000001"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_keys,
                          parse_float=Decimal, parse_constant=reject_constant)
        result = run(obj(data, "input"))
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str, allow_nan=False))
        return 2 if result["status"] == "HOLD" else 0
    except (ValueError, TypeError, OSError, InvalidOperation) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 1

COST_FIELDS = ("product_unit_cost", "platform_fee_per_unit",
               "fulfillment_fee_per_unit", "other_variable_cost_per_unit",
               "expected_return_loss_per_unit")
FIELDS = ("net_unit_revenue", "commission_base_per_unit", *COST_FIELDS,
          "selected_commission_rate", "target_unit_contribution",
          "fixed_campaign_cost", "planned_units")


def run(data):
    scope = obj(data.get("scope"), "scope")
    for key in ("marketplace", "currency", "asin"):
        text(scope.get(key), f"scope.{key}")
    if data.get("model") != "sales_commission":
        raise ValueError("only sales_commission is supported; do not use for CPC")
    for key in ("cost_currency", "revenue_currency"):
        if data.get(key) != scope["currency"]:
            raise ValueError(f"{key}: missing or mixed currency")
    missing = [key for key in FIELDS if data.get(key) is None]
    if missing:
        return {"status": "HOLD", "scope": scope, "missing_fields": missing,
                "unit_contribution": None, "break_even_units": None}
    values = {key: number(data[key], key) for key in FIELDS if key != "planned_units"}
    units = integer(data["planned_units"], "planned_units")
    rate, basis = values["selected_commission_rate"], values["commission_base_per_unit"]
    if rate > 1:
        raise ValueError("selected_commission_rate is a fraction in [0,1], not percent")
    if basis == 0:
        raise ValueError("commission_base_per_unit must be positive")
    variable = sum((values[key] for key in COST_FIELDS), Decimal(0))
    before = values["net_unit_revenue"] - variable
    commission = basis * rate
    contribution = before - commission
    target = values["target_unit_contribution"]
    raw_max = (before - target) / basis
    max_rate = None if raw_max < 0 else min(Decimal(1), raw_max)
    fixed = values["fixed_campaign_cost"]
    break_even = (int((fixed / contribution).to_integral_value(rounding=ROUND_CEILING))
                  if contribution > 0 else None)
    return {"status": "PASS", "scope": scope, "evidence_level": "SCENARIO",
            "variable_cost_before_creator": variable,
            "unit_contribution_before_creator": before,
            "creator_commission_per_unit": commission,
            "unit_contribution": contribution,
            "meets_target_contribution": contribution >= target,
            "max_commission_rate_for_target": max_rate,
            "break_even_units": break_even,
            "planned_commission_spend": commission * units,
            "planned_contribution_after_fixed_cost": contribution * units - fixed,
            "warnings": (["NO_VOLUME_BREAK_EVEN_WITH_NON_POSITIVE_CONTRIBUTION"]
                         if contribution <= 0 else []),
            "platform_eligibility": "NOT_VERIFIED_BY_CALCULATOR",
            "campaign_created": False}


if __name__ == "__main__":
    sys.exit(main())
