# Evaluation README template

Reference only. `rule.md` (OCI-050..057) takes precedence. Write the final README in English and Vietnamese with consistent content.

## Skeleton

```markdown
# <IP family> IP candidates / Các IP ứng viên <IP family>

Assessment basis: document-based review of project README, docs, changelog, and source tree. Not measured or verified.

## Comparison / So sánh

| Item | <IP 1> | <IP 2> |
|---|---|---|
| Source / license | <catalog URL> / <SPDX or text> | ... |
| Features | standards and versions, modes, speeds, widths, channels, parameters, limitations | ... |
| Functions | role, host/bus interface, external interface or PHY, clocking, HDL, dependencies, docs, verification collateral | ... |
| Status | author-stated maturity, last activity, self-reported testing; quote caveats | ... |
| FPGA capability | has run (board/device, speed) / project files only / no evidence found; portability limits | ... |
| ASIC capability | A-D with reason | ... |

### ASIC legend
(reproduce the OCI-054 table)

## Justification per IP / Giải thích đánh giá
## Selection guide / Hướng dẫn chọn theo mục đích
## Special notes / Lưu ý đặc biệt
```

## Style notes

- Cite the file or page each claim comes from (for example `docs/spec.pdf`, project status page).
- Use the exact phrase "no evidence found" where nothing was located.
- `DOWNLOAD_INFO.md` fields: name, catalog URL, upstream URL, download date, revision/archive name, license + URL, archive SHA-256, unavailable or excluded materials.
