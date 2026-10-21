* anova_experiment.sps.
* Experimental manipulation check and outcome comparison.

GET FILE='data/experiment_clean.sav'.
DATASET NAME expdata.

FREQUENCIES VARIABLES=condition attention_check exclusion_flag.

T-TEST GROUPS=condition(0 1)
  /VARIABLES=manipulation_check outcome
  /CRITERIA=CI(.95).

ONEWAY outcome BY condition
  /STATISTICS DESCRIPTIVES HOMOGENEITY
  /POSTHOC=BONFERRONI ALPHA(.05).

UNIANOVA outcome BY condition
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=condition.

GRAPH
  /ERRORBAR(CI 95)=outcome BY condition.
