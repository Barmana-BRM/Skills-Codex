* survey_reliability_factor.sps.
* Replace file paths and variable names before running.

SET DECIMAL=DOT.
SET PRINTBACK=ON.

GET FILE='data/survey_clean.sav'.
DATASET NAME survey.

VARIABLE LABELS
  perf 'Perceived performance'
  ai_use 'AI use intensity'
  trust1 'Trust item 1'
  trust2 'Trust item 2'
  trust3 'Trust item 3'
  autonomy1 'Autonomy item 1'
  autonomy2 'Autonomy item 2'
  autonomy3 'Autonomy item 3'.

MISSING VALUES ALL (-99, -98).

DESCRIPTIVES VARIABLES=perf ai_use trust1 trust2 trust3 autonomy1 autonomy2 autonomy3
  /STATISTICS=MEAN STDDEV MIN MAX SKEWNESS KURTOSIS.

RELIABILITY
  /VARIABLES=trust1 trust2 trust3
  /SCALE('Trust') ALL
  /MODEL=ALPHA
  /STATISTICS=DESCRIPTIVE SCALE CORR.

RELIABILITY
  /VARIABLES=autonomy1 autonomy2 autonomy3
  /SCALE('Autonomy') ALL
  /MODEL=ALPHA
  /STATISTICS=DESCRIPTIVE SCALE CORR.

FACTOR
  /VARIABLES trust1 trust2 trust3 autonomy1 autonomy2 autonomy3
  /MISSING LISTWISE
  /ANALYSIS trust1 trust2 trust3 autonomy1 autonomy2 autonomy3
  /PRINT INITIAL EXTRACTION ROTATION KMO
  /CRITERIA FACTORS(2) ITERATE(25)
  /EXTRACTION PAF
  /CRITERIA MINEIGEN(1)
  /ROTATION OBLIMIN
  /METHOD=CORRELATION.

COMPUTE trust = MEAN(trust1, trust2, trust3).
COMPUTE autonomy = MEAN(autonomy1, autonomy2, autonomy3).
EXECUTE.

CORRELATIONS
  /VARIABLES=perf ai_use trust autonomy
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

SAVE OUTFILE='data/survey_scales.sav'.
