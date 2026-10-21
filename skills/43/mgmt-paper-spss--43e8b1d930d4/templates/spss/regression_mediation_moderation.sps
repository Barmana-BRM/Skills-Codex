* regression_mediation_moderation.sps.
* Hierarchical regression plus mediation/moderation preparation.

GET FILE='data/survey_scales.sav'.
DATASET NAME modeldata.

DESCRIPTIVES VARIABLES=ai_use trust autonomy perf
  /SAVE
  /STATISTICS=MEAN STDDEV MIN MAX.

COMPUTE ai_use_c = ai_use - MEAN(ai_use).
COMPUTE autonomy_c = autonomy - MEAN(autonomy).
COMPUTE interaction_ai_autonomy = ai_use_c * autonomy_c.
EXECUTE.

REGRESSION
  /DEPENDENT perf
  /METHOD=ENTER age gender tenure
  /METHOD=ENTER ai_use trust autonomy
  /STATISTICS COEFF OUTS R ANOVA COLLIN CI(95).

REGRESSION
  /DEPENDENT perf
  /METHOD=ENTER age gender tenure ai_use_c autonomy_c interaction_ai_autonomy
  /STATISTICS COEFF OUTS R ANOVA COLLIN CI(95).

* For mediation or moderated mediation, use PROCESS if installed.
* Example only; confirm model number with theory.
* PROCESS vars=ai_use trust perf autonomy /y=perf /x=ai_use /m=trust /w=autonomy /model=7 /boot=5000 /center=1.

GRAPH
  /SCATTERPLOT(BIVAR)=ai_use WITH perf.
