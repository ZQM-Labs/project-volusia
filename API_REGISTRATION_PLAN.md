# API Key Registration Plan — PROJECT VOLUSIA

## Objective
Register for free API keys to unblock Census ACS, BLS LAUS, and BEA data fetchers.

---

## 1. CENSUS API KEY
**URL:** https://api.census.gov/data/key_signup.html

**Organization:** ZQM Labs / Project Volusia

**Use Case:** Research / Non-commercial research

**Data Access:** ACS 5-Year Estimates (DP03, DP05) for Volusia County

**Steps:**
1. Visit https://api.census.gov/data/key_signup.html
2. Fill in organization name: "ZQM Labs - Project Volusia"
3. Contact email: zqmcomputing@gmail.com
4. Select "Research" use case
5. Review and accept terms
6. Key delivered via email (usually instant)

**Add to .env as:** `CENSUS_API_KEY=your_key_here`

---

## 2. BLS API KEY
**URL:** https://data.bls.gov/registrationEngine/

**Organization:** ZQM Labs / Project Volusia

**Use Case:** Research / Non-commercial use

**Data Access:** Local Area Unemployment Statistics (LAUS) for Volusia County

**Steps:**
1. Visit https://data.bls.gov/registrationEngine/
2. Select "Register for a key"
3. Organization: "ZQM Labs - Project Volusia"
4. Email: zqmcomputing@gmail.com
5. Select "Research" purpose
6. Complete registration (may take 24 hours)

**Add to .env as:** `BLS_API_KEY=your_key_here`

---

## 3. BEA API KEY
**URL:** https://apps.bea.gov/API/signup/index.cfm

**Organization:** ZQM Labs / Project Volusia

**Use Case:** Research

**Data Access:** Local Area Personal Income (CAINC1) for Volusia County

**Steps:**
1. Visit https://apps.bea.gov/API/signup/index.cfm
2. Fill in registration form
3. Organization: "ZQM Labs - Project Volusia"
4. Email: zqmcomputing@gmail.com
5. Select "Research" use case
6. Key delivered via email

**Add to .env as:** `BEA_API_KEY=your_key_here`

---

## 4. POST-REGISTRATION ACTIONS

1. Update `.env` file with all three keys
2. Run full pipeline test: `python run_refresh.py`
3. Verify all 6 fetchers return OK status
4. Commit keys to secure vault (NOT git)
5. Deploy updated .env to production environment

---

## 5. URGENT DECISION NEEDED

The current `.env` file in the project root contains keys. 
Per repository audit, these were flagged for rotation.

**Options:**
- A) Rotate all three keys after initial registration
- B) Use fresh registrations for all keys (cleaner)
- C) Add keys to GitHub Secrets for CI/CD

Recommend: **Option B** - fresh registrations provide clean audit trail.

---

Document owner: ZQM Labs / Project Volusia
Next review: Upon key registration completion