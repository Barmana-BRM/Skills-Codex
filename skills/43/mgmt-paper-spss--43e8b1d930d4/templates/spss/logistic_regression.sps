* logistic_regression.sps.
* Binary outcome model for survey, experiment, or archival coding.

GET FILE='data/binary_outcome_clean.sav'.
DATASET NAME logitdata.

FREQUENCIES VARIABLES=outcome_binary treatment.

LOGISTIC REGRESSION VARIABLES outcome_binary
  /METHOD=ENTER treatment control1 control2 control3
  /CONTRAST (treatment)=Indicator
  /PRINT=CI(95) GOODFIT ITER(1)
  /CRITERIA=PIN(.05) POUT(.10) ITERATE(20) CUT(.5).

* Quality gates:
* - Check sparse cells.
* - Report odds ratios and confidence intervals.
* - Avoid causal language without design support.
