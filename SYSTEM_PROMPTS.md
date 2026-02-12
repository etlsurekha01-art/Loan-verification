# System Prompts Documentation

This document contains all the AI prompts and reasoning logic used in the Agentic AI Loan Verification System. These prompts power the intelligent decision-making agents throughout the loan approval process.

---

## Table of Contents

1. [Critique Agent Prompts](#critique-agent-prompts)
2. [Final Decision Agent Prompts](#final-decision-agent-prompts)
3. [Credit Agent Logic](#credit-agent-logic)
4. [Employment Agent Logic](#employment-agent-logic)
5. [Collateral Agent Logic](#collateral-agent-logic)
6. [Company Verification Prompts](#company-verification-prompts)
7. [Orchestrator Coordination](#orchestrator-coordination)

---

## 1. Critique Agent Prompts

### AI Model: Google Gemini
### Purpose: Quality assurance and risk assessment review

#### Main Critique Prompt

```
You are a Senior Loan Review Officer conducting quality assurance on loan verification results.

Review the following loan application analysis and provide your expert assessment:

APPLICANT INFORMATION:
- Name: {application.name}
- Loan Amount: ${application.loan_amount:,.2f}
- Annual Income: ${application.income:,.2f}
- Credit Score: {application.credit_score}
- Employer: {application.employer}
- Employment Duration: {application.employment_duration} years
- Collateral Value: ${application.collateral_value:,.2f}

VERIFICATION RESULTS:

1. CREDIT ANALYSIS:
{credit_analysis.reasoning}
Risk Score: {credit_analysis.risk_score:.3f}
Status: {credit_analysis.status}

2. EMPLOYMENT VERIFICATION:
{employment_analysis.reasoning}
Verified: {employment_analysis.verified}
Stability: {employment_analysis.stability}

3. COLLATERAL ASSESSMENT:
{collateral_analysis.reasoning}
Adequate: {collateral_analysis.adequate}
LTV Ratio: {collateral_analysis.ltv_ratio:.3f}

PROVIDE YOUR ASSESSMENT:

1. Overall Risk Level (0.0 - 1.0): Provide a single decimal number
2. Confidence Score (0.0 - 1.0): How confident are you in this assessment?
3. Key Concerns: List any red flags or concerns
4. Recommendation: APPROVE, CONDITIONAL, or REJECT

Format your response as JSON:
{
  "risk_level": 0.0-1.0,
  "confidence": 0.0-1.0,
  "concerns": ["concern1", "concern2"],
  "recommendation": "APPROVE|CONDITIONAL|REJECT",
  "reasoning": "Brief explanation"
}
```

#### Fallback Logic (No AI Available)

When Gemini API is unavailable, the system uses deterministic logic:

```python
# Risk aggregation formula
risk_level = (
    credit_analysis.risk_score * 0.40 +  # 40% weight to credit
    employment_risk * 0.35 +              # 35% weight to employment
    collateral_risk * 0.25                # 25% weight to collateral
)

# Confidence based on data completeness
confidence = 1.0  # High confidence in deterministic analysis

# Risk thresholds
if risk_level < 0.3:
    recommendation = "APPROVE"
elif risk_level < 0.6:
    recommendation = "CONDITIONAL"
else:
    recommendation = "REJECT"
```

---

## 2. Final Decision Agent Prompts

### AI Model: Google Gemini
### Purpose: Make final loan approval decision with detailed reasoning

#### Main Decision Prompt

```
You are the Chief Loan Officer making the final decision on a loan application.

APPLICANT: {application.name}
REQUESTED LOAN: ${application.loan_amount:,.2f}

COMPLETE ANALYSIS:

CREDIT PROFILE:
- Credit Score: {application.credit_score}
- Risk Assessment: {credit_analysis.risk_score:.3f}
- Status: {credit_analysis.status}
- Details: {credit_analysis.reasoning}

EMPLOYMENT STATUS:
- Employer: {application.employer}
- Duration: {application.employment_duration} years
- Annual Income: ${application.income:,.2f}
- Verified: {employment_analysis.verified}
- Stability: {employment_analysis.stability}
- Details: {employment_analysis.reasoning}

COLLATERAL:
- Value: ${application.collateral_value:,.2f}
- Loan-to-Value: {collateral_analysis.ltv_ratio:.1%}
- Adequate: {collateral_analysis.adequate}
- Details: {collateral_analysis.reasoning}

QUALITY REVIEW:
- Risk Level: {critique.risk_level:.3f}
- Confidence: {critique.confidence:.3f}
- Concerns: {', '.join(critique.concerns)}
- Recommendation: {critique.recommendation}

MAKE YOUR DECISION:

1. Decision: APPROVE, CONDITIONAL, or REJECT
2. Overall Risk Score (0.0 - 1.0): Provide single decimal number
3. Detailed Reasoning: Explain your decision
4. Conditions (if conditional): List any conditions that must be met
5. Recommendations: Any advice for the applicant

Format your response as JSON:
{
  "decision": "APPROVE|CONDITIONAL|REJECT",
  "risk_score": 0.0-1.0,
  "reasoning": "Detailed explanation",
  "conditions": ["condition1", "condition2"],
  "recommendations": ["recommendation1", "recommendation2"]
}
```

#### Fallback Logic (No AI Available)

```python
# Decision tree logic
if critique.recommendation == "APPROVE":
    decision = LoanDecision.APPROVED
elif critique.recommendation == "CONDITIONAL":
    decision = LoanDecision.CONDITIONAL
else:
    decision = LoanDecision.REJECTED

# Risk calculation
risk_score = critique.risk_level

# Generate deterministic reasoning
if decision == LoanDecision.APPROVED:
    reasoning = f"Application approved. Strong financial profile with credit score {credit_score}, {employment_duration} years employment, and adequate collateral (LTV: {ltv_ratio:.1%})."
elif decision == LoanDecision.CONDITIONAL:
    reasoning = f"Conditional approval. Moderate risk profile. Additional verification or guarantor may be required."
else:
    reasoning = f"Application rejected. Risk factors exceed acceptable thresholds."
```

---

## 3. Credit Agent Logic

### Purpose: Deterministic credit risk analysis (No AI)

#### Credit Scoring Algorithm

```python
# Risk components calculation
EXCELLENT_THRESHOLD = 750
GOOD_THRESHOLD = 700
FAIR_THRESHOLD = 650
POOR_THRESHOLD = 600

# Base risk from credit score (60% weight)
if credit_score >= EXCELLENT_THRESHOLD:
    score_risk = 0.05  # Excellent: 5% risk
elif credit_score >= GOOD_THRESHOLD:
    score_risk = 0.15  # Good: 15% risk
elif credit_score >= FAIR_THRESHOLD:
    score_risk = 0.35  # Fair: 35% risk
elif credit_score >= POOR_THRESHOLD:
    score_risk = 0.60  # Poor: 60% risk
else:
    score_risk = 0.85  # Very Poor: 85% risk

# Debt-to-Income ratio risk (40% weight)
monthly_income = income / 12
monthly_payment = loan_amount * (0.06 / 12) / (1 - (1 + 0.06/12)^(-360))
dti_ratio = monthly_payment / monthly_income

if dti_ratio > 0.43:
    dti_risk = 0.80  # High risk
elif dti_ratio > 0.36:
    dti_risk = 0.50  # Moderate risk
elif dti_ratio > 0.28:
    dti_risk = 0.25  # Low-moderate risk
else:
    dti_risk = 0.10  # Low risk

# Combined risk score
total_risk = (score_risk * 0.60) + (dti_risk * 0.40)
```

#### Credit Status Classification

```python
if total_risk < 0.25:
    status = "Excellent"
    rating = "Low risk borrower with strong credit profile"
elif total_risk < 0.40:
    status = "Good"
    rating = "Above-average credit profile with manageable risk"
elif total_risk < 0.60:
    status = "Fair"
    rating = "Average credit profile with moderate risk"
else:
    status = "Poor"
    rating = "Below-average credit profile with elevated risk"
```

---

## 4. Employment Agent Logic

### Purpose: Employment verification and income stability analysis (Deterministic + API)

#### LinkedIn Profile Verification Logic

```python
# Profile Completeness Assessment (0-100%)
completeness_factors = {
    "has_linkedin_url": 30,      # 30 points
    "has_job_title": 20,          # 20 points
    "has_employment_type": 15,    # 15 points
    "has_professional_email": 20, # 20 points
    "has_previous_employers": 15  # 15 points
}

profile_completeness = sum(points for factor, points in factors.items() if present)

# Verification confidence
if profile_completeness >= 80:
    confidence = "High"
elif profile_completeness >= 50:
    confidence = "Medium"
else:
    confidence = "Low"
```

#### Employment History Verification

```python
# Job Stability Score
STABILITY_THRESHOLDS = {
    "excellent": 3.0,  # 3+ years
    "good": 1.5,       # 1.5-3 years
    "fair": 0.5,       # 0.5-1.5 years (0.5 with LinkedIn, 1.0 without)
    "poor": 0.0        # < threshold
}

# Previous employers analysis
if previous_employers:
    avg_tenure = employment_duration / (len(previous_employers) + 1)
    if avg_tenure >= 2.0:
        job_hopping_risk = "Low"
    elif avg_tenure >= 1.0:
        job_hopping_risk = "Moderate"
    else:
        job_hopping_risk = "High"
```

#### Professional Credentials Assessment

```python
# Job Title Analysis
senior_titles = ["senior", "lead", "principal", "director", "manager", "vp", "chief"]
is_senior_role = any(title in job_title.lower() for title in senior_titles)

# Employment Type
full_time_preferred = employment_type in ["Full-time", "Permanent"]

# Corporate Email
has_corporate_email = professional_email and "@gmail" not in email and "@yahoo" not in email

# Credentials Score
credentials_score = (
    (30 if is_senior_role else 10) +
    (30 if full_time_preferred else 15) +
    (40 if has_corporate_email else 10)
)
```

#### Company Verification (Serper API Integration)

```python
# Simulated LinkedIn Check (when API not available)
KNOWN_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Meta",
    "Netflix", "Tesla", "Salesforce", "Oracle", "IBM",
    "Intel", "AMD", "Nvidia", "Adobe", "Cisco"
]

if company in KNOWN_COMPANIES:
    return {
        "found": True,
        "profile_url": f"https://www.linkedin.com/company/{company.lower()}",
        "confidence": "simulated"
    }
```

#### Employment Risk Calculation

```python
# Risk factors
base_risk = 0.30 if not verified else 0.10
stability_risk = {
    "Excellent": 0.05,
    "Good": 0.15,
    "Fair": 0.30,
    "Poor": 0.50
}[stability_rating]

# Risk flags
flags = []
if employment_duration < employment_threshold:
    flags.append("short_employment")
if not verified:
    flags.append("unverified_employer")
if not linkedin_profile_found:
    flags.append("no_linkedin_profile")

# Final risk score
employment_risk = min(base_risk + stability_risk + (len(flags) * 0.10), 1.0)
```

---

## 5. Collateral Agent Logic

### Purpose: Collateral adequacy assessment (Deterministic)

#### Loan-to-Value (LTV) Calculation

```python
# LTV ratio formula
ltv_ratio = loan_amount / collateral_value

# Industry standard thresholds
EXCELLENT_LTV = 0.60  # 60% or less
GOOD_LTV = 0.70       # 60-70%
FAIR_LTV = 0.80       # 70-80%
ACCEPTABLE_LTV = 0.90 # 80-90%
HIGH_LTV = 0.95       # 90-95%
```

#### Collateral Risk Assessment

```python
# Risk classification
if ltv_ratio <= EXCELLENT_LTV:
    risk_level = 0.10
    rating = "Excellent"
    reasoning = "Very strong collateral position with significant equity cushion"
elif ltv_ratio <= GOOD_LTV:
    risk_level = 0.20
    rating = "Good"
    reasoning = "Good collateral coverage with adequate protection"
elif ltv_ratio <= FAIR_LTV:
    risk_level = 0.35
    rating = "Fair"
    reasoning = "Acceptable collateral coverage meeting standard requirements"
elif ltv_ratio <= ACCEPTABLE_LTV:
    risk_level = 0.55
    rating = "Marginal"
    reasoning = "Marginal collateral coverage with limited equity buffer"
elif ltv_ratio <= HIGH_LTV:
    risk_level = 0.75
    rating = "High Risk"
    reasoning = "High LTV ratio presents elevated risk exposure"
else:
    risk_level = 0.90
    rating = "Very High Risk"
    reasoning = "Excessive LTV ratio exceeds prudent lending standards"
```

#### Collateral Adequacy Decision

```python
# Adequacy threshold
MAXIMUM_ACCEPTABLE_LTV = 0.90  # 90%

if ltv_ratio <= MAXIMUM_ACCEPTABLE_LTV:
    adequate = True
else:
    adequate = False
    reasoning += ". CRITICAL: Loan amount exceeds acceptable collateral value."
```

---

## 6. Company Verification Prompts (Serper API)

### Purpose: Real-time company verification using web search

#### Search Query Construction

```python
# Serper API search query
query = f"{company_name} company official website"

# API Request
{
    "q": query,
    "num": 3,  # Top 3 results
    "gl": "us" # Geographic location: United States
}
```

#### Result Analysis Algorithm

```python
# Positive Indicators
positive_keywords = [
    "official", "website", "company", "corporation", "inc", "ltd",
    "registered", "founded", "headquarters", "employees", "ceo",
    "about us", "careers", "contact", "business"
]

# Context-Aware Negative Patterns
negative_patterns = [
    f"{company_name} scam",
    f"{company_name} fraud",
    "is a scam",
    "is fraud",
    "is fake",
    "company is not legitimate",
    "known scam",
    "fraudulent company"
]

# Scam Checking Sites (Suspicious if predominant)
scam_checking_keywords = [
    "scamadviser",
    "is scam",
    "check if",
    "legit or scam",
    "reported scam",
    "fraud database"
]

# Trusted Sources
trusted_domains = [
    "wikipedia.org",
    "linkedin.com",
    "bloomberg.com",
    "forbes.com",
    "bbb.org",
    "sec.gov"
]
```

#### Verification Decision Logic

```python
# Check for official presence
has_official_site = any(
    company_name.lower().replace(" ", "") in result["link"].lower()
    for result in results
)

has_trusted_source = any(
    any(domain in result["link"] for domain in trusted_domains)
    for result in results
)

is_scam_checking = sum(
    1 for result in results
    if any(keyword in result_text.lower() for keyword in scam_checking_keywords)
)

# Decision tree
if negative_indicators > 2:
    verified = False
    confidence = "high"
    reason = "Negative indicators found in search results"
elif has_official_site or has_trusted_source:
    verified = True
    confidence = "high"
    reason = "Company appears legitimate based on search results"
elif is_scam_checking >= 2:
    verified = False
    confidence = "low"
    reason = "Company verification inconclusive - insufficient legitimate sources"
elif positive_indicators >= 7:
    verified = True
    confidence = "high"
elif positive_indicators >= 4:
    verified = True
    confidence = "medium"
else:
    verified = False
    confidence = "low"
    reason = "Insufficient verification information"
```

---

## 7. Orchestrator Coordination

### Purpose: Coordinate multi-agent workflow

#### Agent Execution Sequence

```python
# Stage 1: Greeting and Planning
greeting_result = GreetingAgent.process(application)
plan = PlannerAgent.create_plan(application)

# Stage 2: Parallel Verification (concurrent execution)
credit_task = asyncio.create_task(CreditAgent.process(application))
employment_task = asyncio.create_task(EmploymentAgent.process(application))
collateral_task = asyncio.create_task(CollateralAgent.process(application))

credit_result, employment_result, collateral_result = await asyncio.gather(
    credit_task, employment_task, collateral_task
)

# Stage 3: Quality Review
critique_result = await CritiqueAgent.process(
    application, credit_result, employment_result, collateral_result
)

# Stage 4: Final Decision
final_decision = await FinalDecisionAgent.process(
    application, credit_result, employment_result, collateral_result, critique_result
)
```

#### Task Status Tracking

```python
# Database task states
TASK_STATES = {
    "pending": "Task created, awaiting processing",
    "in_progress": "Agents actively processing",
    "completed": "All verification complete",
    "failed": "Error occurred during processing"
}

# Progress tracking
stages = [
    "Greeting and Planning",
    "Parallel Verification",
    "Quality Review",
    "Final Decision"
]
```

---

## 8. Simple Loan Eligibility Logic

### Purpose: Fast eligibility check with Serper API

#### Basic Eligibility Rules

```python
# Minimum requirements
MIN_CREDIT_SCORE = 650
MIN_ANNUAL_INCOME = 30000

# Step 1: Validate input (Pydantic models)

# Step 2: Check credit score
if credit_score < MIN_CREDIT_SCORE:
    return REJECTED(f"Credit score {credit_score} below minimum {MIN_CREDIT_SCORE}")

# Step 3: Check income
if income < MIN_ANNUAL_INCOME:
    return REJECTED(f"Income ${income:,.2f} below minimum ${MIN_ANNUAL_INCOME:,.2f}")

# Step 4: Verify company (Serper API)
verification = SerperService.verify_company(company)

# Step 5: Final decision
if verification["verified"]:
    return APPROVED(
        f"Credit score is {credit_score}, income meets requirements (${income:,.2f}), "
        f"and company {company} has been verified as legitimate "
        f"({verification['confidence']} confidence). {verification['reason']}"
    )
else:
    return REJECTED(
        f"While credit score ({credit_score}) and income (${income:,.2f}) meet requirements, "
        f"company verification failed: {verification['reason']}"
    )
```

---

## 9. Prompt Engineering Best Practices

### Guidelines Used in This System

1. **Clear Role Definition**: Each prompt starts with "You are a [specific role]"
2. **Structured Input**: Data presented in clear sections (APPLICANT, ANALYSIS, etc.)
3. **Explicit Output Format**: JSON schema specified for consistent parsing
4. **Context Provision**: All relevant data included for informed decisions
5. **Fallback Logic**: Deterministic alternatives when AI unavailable
6. **Numerical Constraints**: Risk scores explicitly bounded (0.0 - 1.0)
7. **Decision Options**: Limited choices (APPROVE, CONDITIONAL, REJECT)
8. **Reasoning Required**: Always ask for explanation of decisions
9. **Multi-Factor Analysis**: Consider multiple data points
10. **Risk-Aware**: Explicitly focus on risk assessment and mitigation

### Prompt Optimization Techniques

```python
# Template structure
PROMPT_TEMPLATE = """
[ROLE DEFINITION]
You are a [specific expert role] with [relevant expertise].

[CONTEXT SECTION]
Here is the information you need to analyze:
- [Data Point 1]
- [Data Point 2]
...

[ANALYSIS SECTION]
Previous assessments:
1. [Assessment 1]: [Results]
2. [Assessment 2]: [Results]

[TASK DEFINITION]
Provide the following:
1. [Output 1]: [Format/constraints]
2. [Output 2]: [Format/constraints]

[OUTPUT FORMAT]
Format as JSON:
{
  "field1": "value",
  "field2": 0.0-1.0,
  ...
}
"""
```

---

## 10. API Integration Patterns

### Gemini API Integration

```python
# Model configuration
model = genai.GenerativeModel("gemini-pro")
generation_config = {
    "temperature": 0.7,       # Balanced creativity/consistency
    "top_p": 0.8,            # Nucleus sampling
    "top_k": 40,             # Top-k sampling
    "max_output_tokens": 1024 # Response length limit
}

# Error handling
try:
    response = model.generate_content(prompt)
    result = json.loads(response.text)
except Exception as e:
    logger.error(f"AI error: {e}")
    # Fall back to deterministic logic
    result = fallback_logic()
```

### Serper API Integration

```python
# API configuration
SERPER_API_URL = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

# Search request
payload = {
    "q": search_query,
    "num": 3  # Top 3 results
}

# Error handling with simulation fallback
try:
    response = requests.post(SERPER_API_URL, json=payload, headers=headers, timeout=10)
    data = response.json()
    return analyze_results(data["organic"])
except Exception as e:
    logger.warning(f"Serper API error: {e}, using simulation")
    return simulate_company_check(company_name)
```

---

## 11. Decision Reasoning Examples

### Example 1: Approved Application

```
DECISION: APPROVED
RISK SCORE: 0.249

REASONING:
Strong approval factors:
- Excellent credit score (750) indicates reliable payment history
- Stable employment (5+ years) with verified employer (Google)
- Conservative loan-to-value ratio (60%) provides substantial equity cushion
- LinkedIn profile verified with senior job title
- Professional credentials confirmed

Overall Assessment: Low-risk borrower with exceptional financial profile. 
Recommend standard approval with competitive interest rate.
```

### Example 2: Conditional Approval

```
DECISION: CONDITIONAL
RISK SCORE: 0.465

REASONING:
Mixed factors requiring additional review:
- Fair credit score (680) - acceptable but not excellent
- Adequate collateral (75% LTV) but limited equity buffer
- Employment duration borderline (1.5 years)
- Income sufficient but DTI ratio at 38%

CONDITIONS:
1. Provide additional 2 years of employment history
2. Consider co-signer or guarantor
3. Increase down payment to achieve 70% LTV

With conditions met, risk would decrease to acceptable levels.
```

### Example 3: Rejected Application

```
DECISION: REJECTED
RISK SCORE: 0.782

REASONING:
Multiple critical risk factors:
- Poor credit score (580) indicates payment difficulties
- High debt-to-income ratio (52%) suggests overextension
- Insufficient collateral (92% LTV) provides minimal protection
- Short employment duration (0.5 years) lacks stability
- Company verification failed - no legitimate sources found

Overall Assessment: Risk level exceeds acceptable thresholds for approval. 
Recommend applicant improve credit profile and employment stability before reapplying.

RECOMMENDATIONS:
1. Focus on improving credit score to 650+ range
2. Reduce existing debt obligations
3. Establish 2+ years employment history
4. Increase down payment to reduce LTV to 80% or below
```

---

## 12. System Prompt Versioning

### Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Feb 2026 | Initial system with basic credit/employment/collateral logic | System |
| 1.1 | Feb 2026 | Added LinkedIn profile verification | System |
| 1.2 | Feb 2026 | Integrated Serper.dev API for company verification | System |
| 1.3 | Feb 2026 | Enhanced context-aware negative indicator detection | System |
| 1.4 | Feb 2026 | Added trusted domain verification and official site detection | System |

### Configuration Management

```python
# Prompt version tracking
PROMPT_VERSION = "1.4"
LAST_UPDATED = "2026-02-12"

# Model configurations
AI_MODELS = {
    "critique": "gemini-pro",
    "decision": "gemini-pro"
}

# API endpoints
APIS = {
    "gemini": "https://generativelanguage.googleapis.com",
    "serper": "https://google.serper.dev/search"
}
```

---

## 13. Testing and Validation

### Prompt Testing Scenarios

```python
# Test cases for each agent
TEST_SCENARIOS = {
    "excellent_profile": {
        "credit_score": 780,
        "income": 120000,
        "employment_duration": 8,
        "collateral_value": 100000,
        "loan_amount": 50000,
        "expected_decision": "APPROVED"
    },
    "marginal_profile": {
        "credit_score": 670,
        "income": 45000,
        "employment_duration": 1.5,
        "collateral_value": 40000,
        "loan_amount": 30000,
        "expected_decision": "CONDITIONAL"
    },
    "poor_profile": {
        "credit_score": 580,
        "income": 25000,
        "employment_duration": 0.3,
        "collateral_value": 20000,
        "loan_amount": 25000,
        "expected_decision": "REJECTED"
    }
}
```

---

## Conclusion

This document captures all the intelligent reasoning, decision logic, and prompts that power the Agentic AI Loan Verification System. The system combines:

- **AI-Powered Reasoning**: Gemini API for nuanced critique and final decisions
- **Deterministic Logic**: Mathematical formulas for credit, employment, and collateral analysis
- **Real-Time Verification**: Serper.dev API for company verification
- **Fallback Mechanisms**: Simulation logic when APIs unavailable
- **Multi-Agent Architecture**: Specialized agents working in parallel

The prompts are designed for:
- ✅ Consistency: Structured JSON outputs
- ✅ Explainability: Always provide reasoning
- ✅ Risk Awareness: Explicit risk scoring
- ✅ Fallback Safety: Deterministic alternatives
- ✅ Real-Time Data: Live web search integration

**Last Updated**: February 12, 2026
**System Version**: 1.4
**Total Prompts**: 13 major categories
**AI Models**: Google Gemini (gemini-pro)
**External APIs**: Serper.dev (company verification)
