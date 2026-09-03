METHODOLOGY DOCUMENTATION — PROJECT VOLUSIA
=============================================
Project Volusia — Methodology Folder Index

Version: 1.0
Date: 2026-09-02

---

1. PURPOSE
===========

This folder contains the methodologies used by Project Volusia for
data collection, analysis, research, and reporting. Every method is
documented so that:

   - Our work is reproducible by others
   - Our limitations are clearly stated
   - Our findings can be challenged and improved
   - We maintain consistency across reports and over time

---

2. DATA COLLECTION METHODOLOGY
===============================

2.1 SOURCE SELECTION CRITERIA
-------------------------------
We select data sources based on:

  AUTHORITY       — Is the source the primary collector of this data?
                  (e.g., Census for demographics, BLS for employment)

  METHODOLOGY     — Does the source document how data is collected?
                  Is the methodology sound and transparent?

  COVERAGE        — Does the data cover Volusia County specifically?
                  Is the geographic resolution sufficient?

  TIMELINESS      — How frequently is the data updated? Is the
                  most recent version available?

  ACCESSIBILITY   — Is the data available in machine-readable format?
                  Is there an API?

  LICENSE         — Is the data public domain or openly licensed?
                  Are there usage restrictions?

  HISTORY         — Has the source been consistent over time?
                  Can we build longitudinal datasets?

2.2 DATA ACQUISITION PROCESS
------------------------------

  Step 1: IDENTIFY
    - Define the question or indicator needed
    - Identify potential sources
    - Evaluate sources against selection criteria
    - Document the chosen source and rationale

  Step 2: ACQUIRE
    - Download via API, direct download, or (as last resort) scraping
    - Record the date and time of access
    - Record the version or vintage of the data
    - Store the raw, unmodified original

  Step 3: VALIDATE
    - Check for completeness (expected rows/columns present?)
    - Check for anomalies (out-of-range values, duplicates)
    - Cross-reference with previous vintage if available
    - Document any issues found

  Step 4: DOCUMENT
    - Record source URL, date accessed, license
    - Record any known limitations or caveats
    - Record the intended use case

2.3 DATA QUALITY ASSESSMENT
-----------------------------

Every dataset is assessed on:

  COMPLETENESS    — What percentage of expected data is present?
                  Are there systematic gaps?

  ACCURACY        — Does the data match reality where we can verify?
                  Are there known error rates?

  CONSISTENCY     — Is the data internally consistent? Does it
                  agree with related datasets?

  TIMELINESS      — How old is the data? Is it fit for the
                  intended purpose?

  ACCESSIBILITY   — Can stakeholders actually access this data?
                  Is it in a usable format?

  Quality scores (1-5) are recorded for each dimension.

---

3. ANALYSIS METHODOLOGY
=========================

3.1 DESCRIPTIVE ANALYSIS
-------------------------
We start every analysis with description:

  - Central tendency (mean, median, mode)
  - Dispersion (standard deviation, IQR, range)
  - Distribution shape (histogram, density plot)
  - Temporal trends (time series plot)
  - Geographic distribution (map)

  Description is not the end goal. It is the foundation that
  prevents us from jumping to wrong conclusions.

3.2 CORRELATION ANALYSIS
-------------------------
When examining relationships between variables:

  - We calculate Pearson (linear) or Spearman (monotonic) correlation
  - We report confidence intervals, not just point estimates
  - We test for statistical significance (p-values with caveats
    about what they mean and don't mean)
  - We visualize the relationship (scatter plot)
  - We explicitly state: correlation does not imply causation

3.3 REGRESSION ANALYSIS
-------------------------
When modeling relationships:

  - We specify the model form and justify it
  - We report coefficients, standard errors, p-values, and R-squared
  - We check residuals for normality, homoscedasticity, independence
  - We test for multicollinearity (VIF)
  - We validate with holdout data or cross-validation where possible
  - We state assumptions and limitations

3.4 TIME SERIES FORECASTING
-----------------------------
When projecting future values:

  - We test for stationarity (ADF test)
  - We identify seasonality and trend components
  - We select model (ARIMA, ETS, Prophet) based on data properties
  - We report prediction intervals, not just point forecasts
  - We back-test against historical data
  - We state the horizon over which the model is reliable
  - We track forecast accuracy over time and report it publicly

3.5 GEOSPATIAL ANALYSIS
-------------------------
When analyzing geographic patterns:

  - We use appropriate coordinate reference systems (EPSG:4269 for
    census, local State Plane for precision)
  - We account for spatial autocorrelation where relevant
  - We use appropriate geographic units (tract, zip, city, county)
    based on the question
  - We avoid ecological fallacy (assuming group-level patterns
    apply to individuals)

3.6 MACHINE LEARNING
----------------------
When using ML models:

  - We justify why ML is needed (vs. simpler methods)
  - We document feature engineering
  - We split data into training/validation/test sets
  - We report multiple metrics (accuracy, precision, recall, F1,
    AUC-ROC for classification; RMSE, MAE, MAPE for regression)
  - We check for overfitting
  - We assess feature importance
  - We evaluate for bias (across geographies, demographics)
  - We document model version, hyperparameters, and training data

---

4. MARKET RESEARCH METHODOLOGY
================================

4.1 SURVEY DESIGN
-----------------
When we conduct or commission surveys:

  QUESTIONNAIRE
    - Questions are neutral (not leading)
    - Response options are exhaustive and mutually exclusive
    - We avoid double-barreled questions
    - We pilot-test before full deployment

  SAMPLING
    - We define the target population precisely
    - We use probability sampling where possible
    - We calculate required sample size for desired confidence
      level and margin of error
    - We document response rate and non-response bias

  ADMINISTRATION
    - We choose mode (phone, online, in-person) based on population
    - We document timing and context
    - We protect respondent privacy

4.2 INTERVIEW METHODOLOGY
---------------------------
For expert interviews and stakeholder interviews:

  - We prepare a semi-structured guide (not a rigid script)
  - We document the interviewee's role and perspective
  - We record (with consent) and transcribe
  - We identify themes across interviews
  - We distinguish between an interviewee's opinion and verified fact

4.3 FACILITATED SESSIONS
--------------------------
For focus groups and community meetings:

  - We define the purpose and scope in advance
  - We recruit diverse participants
  - We use a trained facilitator
  - We document themes, not just individual quotes
  - We report the limitations (small sample, self-selection)

4.4 OBSERVATIONAL RESEARCH
-----------------------------
For direct observation (visitor behavior, business operations, etc.):

  - We define what we are observing and why
  - We use a structured observation protocol
  - We document observer bias potential
  - We distinguish between what we observed and what we inferred

---

5. REPORTING METHODOLOGY
==========================

5.1 VISUALIZATION STANDARDS
-----------------------------

  - Every chart has a clear title describing what is shown
  - Axes are labeled with units
  - Data source is cited below the chart
  - Color choices are accessible (colorblind-safe palettes)
  - We avoid distorting scales (no truncated y-axis to exaggerate)
  - We use the chart type that best represents the data:
      Line   → trends over time
      Bar    → comparisons across categories
      Scatter → relationships between two variables
      Map    → geographic distribution
      Heatmap → matrix patterns

5.2 NARRATIVE STANDARDS
-------------------------

  - We lead with the finding, then show the evidence
  - We use precise language:
      "increased by 5%" not "increased significantly"
      "correlation of 0.7" not "strong relationship"
      "p=0.03" not "statistically significant" (without context)
  - We avoid hedging language that obscures meaning ("may,"
    "could," "might" — unless uncertainty is genuine)
  - We state confidence levels honestly

5.3 UNCERTAINTY COMMUNICATION
-------------------------------

  - We distinguish between:
      Known facts (with source)
      Estimates (with confidence intervals)
      Projections (with assumptions stated)
      Opinions (labeled as such)
  - We use ranges, not false precision
  - We say "we don't know" when we don't know

---

6. ETHICAL METHODOLOGY
========================

6.1 PRIVACY PROTECTION
-----------------------
  - We never publish personally identifiable information (PII)
  - We aggregate data before release (minimum cell sizes)
  - We use differential privacy techniques where appropriate
  - We comply with HIPAA, FERPA, CCPA, and Florida law

6.2 BIAS AWARENESS
-------------------
  - We acknowledge our own biases and how they might affect analysis
  - We test for sampling bias, selection bias, confirmation bias
  - We seek disconfirming evidence
  - We include diverse perspectives in review

6.3 CONFLICT OF INTEREST
-------------------------
  - We disclose funding sources for all research
  - We disclose relationships with data providers
  - We maintain editorial independence from funders
  - We publish findings even when they are uncomfortable

---

7. REPRODUCIBILITY STANDARDS
==============================

  - Every analysis has a documented method
  - Every dataset has a recorded source and vintage
  - Every transformation is documented (scripts, not just descriptions)
  - Every report includes a methodology section
  - Code is version-controlled
  - Another analyst could reproduce our work from our documentation

---

Document owner: Project Volusia Research Team
Related: ../COMMERCE_RESEARCH_RELIABILITY.md, ../OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md
