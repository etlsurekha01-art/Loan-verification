# Serper.dev API Integration Guide

## Overview

The Agentic AI Loan Verification System now includes **real web search** capabilities using **Serper.dev API** for company verification. This provides authentic, real-time information about employers during the loan verification process.

---

## 🎯 Features

### New `/check-loan-eligibility` Endpoint

A simplified loan eligibility check with the following flow:

```
1. Validate Input → 2. Check Credit Score → 3. Check Income → 4. Verify Company → 5. Final Decision
```

**Key Features:**
- ✅ **Fast Decision**: Streamlined eligibility logic
- ✅ **Real Company Verification**: Uses Serper.dev API for Google search results
- ✅ **Confidence Scoring**: High/Medium/Low confidence ratings
- ✅ **Fallback Simulation**: Works without API key (simulation mode)
- ✅ **Search Results**: Returns top 3 search results for verification

---

## 📋 API Endpoint Details

### POST `/check-loan-eligibility`

**Request Body:**
```json
{
  "name": "John Smith",
  "income": 75000,
  "company": "Google",
  "loan_amount": 25000,
  "credit_score": 720
}
```

**Response:**
```json
{
  "status": "APPROVED",
  "reason": "Credit score is 720, income meets requirements ($75,000.00), and company Google has been verified as legitimate (high confidence). Found 3 legitimate sources confirming company existence.",
  "verification_results": [
    {
      "title": "Google - Official Website",
      "snippet": "Google is a well-known technology company...",
      "link": "https://www.google.com"
    }
  ],
  "company_verified": true,
  "verification_confidence": "high"
}
```

**Response Fields:**
- `status`: "APPROVED" or "REJECTED"
- `reason`: Detailed explanation for the decision
- `verification_results`: Array of search results (max 3)
- `company_verified`: Boolean indicating if company was verified
- `verification_confidence`: "high", "medium", "low", or "simulated"

---

## 🔑 Getting Started with Serper.dev API

### Step 1: Get Your API Key

1. Go to [https://serper.dev](https://serper.dev)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

### Step 2: Configure Environment

Add your Serper API key to the `.env` file:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here  # <-- Add this line
```

### Step 3: Restart the Server

```bash
# Kill existing server
pkill -f uvicorn

# Start new server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing the Endpoint

### Test Script

Run the included test script:

```bash
python test_simple_endpoint.py
```

### Manual Testing with cURL

**APPROVED Case:**
```bash
curl -X POST "http://localhost:8000/check-loan-eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "income": 75000,
    "company": "Google",
    "loan_amount": 25000,
    "credit_score": 720
  }'
```

**REJECTED Case (Low Credit):**
```bash
curl -X POST "http://localhost:8000/check-loan-eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "income": 80000,
    "company": "Microsoft",
    "loan_amount": 30000,
    "credit_score": 600
  }'
```

**REJECTED Case (Suspicious Company):**
```bash
curl -X POST "http://localhost:8000/check-loan-eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Brown",
    "income": 50000,
    "company": "XYZ Fake Corp 12345",
    "loan_amount": 20000,
    "credit_score": 680
  }'
```

---

## 🔬 How Company Verification Works

### With Serper API (Real Mode)

When API key is configured:

1. **Search Query**: Queries Google via Serper API for the company name
2. **Result Analysis**: Analyzes top 3 search results
3. **Indicator Detection**: 
   - **Positive**: "official", "website", "company", "corporation", "founded", "headquarters"
   - **Negative**: "scam", "fraud", "fake", "not legitimate", "warning"
4. **Confidence Scoring**:
   - **High**: 3+ positive indicators, no negative indicators
   - **Medium**: 1-2 positive indicators, no negative indicators
   - **Low**: Few positive or any negative indicators
5. **Decision**: Company verified if confidence is "high" or "medium"

### Without Serper API (Simulation Mode)

When API key is NOT configured:

1. **Fallback Mode**: Uses known company list simulation
2. **Known Companies**: Google, Microsoft, Amazon, Apple, Meta, Netflix, Tesla, etc.
3. **Confidence**: Always returns "simulated"
4. **Results**: Returns mock search results for testing

---

## 📊 Eligibility Logic

### Minimum Requirements

- **Credit Score**: ≥ 650
- **Annual Income**: ≥ $30,000
- **Company Verification**: Must pass verification

### Decision Flow

```
┌─────────────────┐
│  Input Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     NO    ┌──────────┐
│ Credit ≥ 650?   ├──────────►│ REJECTED │
└────────┬────────┘            └──────────┘
         │ YES
         ▼
┌─────────────────┐     NO    ┌──────────┐
│ Income ≥ 30K?   ├──────────►│ REJECTED │
└────────┬────────┘            └──────────┘
         │ YES
         ▼
┌─────────────────┐
│ Verify Company  │
│  (Serper API)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│APPROVED│ │ REJECTED │
└────────┘ └──────────┘
```

---

## 🛠️ Files Added/Modified

### New Files Created

1. **`serper_service.py`** - Serper.dev API integration service
2. **`simple_loan_models.py`** - Pydantic models for simple endpoint
3. **`test_simple_endpoint.py`** - Automated test suite
4. **`SERPER_INTEGRATION.md`** - This documentation

### Modified Files

1. **`main.py`** - Added `/check-loan-eligibility` endpoint
2. **`requirements.txt`** - Added `requests==2.31.0`
3. **`.env`** - Added `SERPER_API_KEY` configuration

---

## 🔍 API Response Examples

### ✅ APPROVED

```json
{
  "status": "APPROVED",
  "reason": "Credit score is 720, income meets requirements ($75,000.00), and company Google has been verified as legitimate (high confidence). Found 3 legitimate sources.",
  "verification_results": [
    {
      "title": "Google - About",
      "snippet": "Google LLC is an American multinational technology company...",
      "link": "https://about.google/"
    },
    {
      "title": "Google - Wikipedia",
      "snippet": "Google is a search engine founded in 1998...",
      "link": "https://en.wikipedia.org/wiki/Google"
    }
  ],
  "company_verified": true,
  "verification_confidence": "high"
}
```

### ❌ REJECTED (Low Credit Score)

```json
{
  "status": "REJECTED",
  "reason": "Credit score 600 is below minimum requirement of 650",
  "verification_results": [],
  "company_verified": false,
  "verification_confidence": "n/a"
}
```

### ❌ REJECTED (Company Not Verified)

```json
{
  "status": "REJECTED",
  "reason": "While credit score (680) and income ($50,000.00) meet requirements, company verification failed: Unable to find sufficient legitimate sources for company verification.",
  "verification_results": [],
  "company_verified": false,
  "verification_confidence": "low"
}
```

---

## 💡 Usage Tips

1. **Free Tier**: Serper.dev offers 2,500 free searches per month
2. **Rate Limiting**: Built-in error handling for API rate limits
3. **Fallback Mode**: System works without API key for development/testing
4. **Company Names**: More specific company names yield better results
5. **Cache Results**: Consider caching verification results to save API calls

---

## 🚀 Next Steps

### Enhance Company Verification

You can further improve company verification by:

1. **Adding to Employment Agent**: Integrate `serper_service.py` into the full multi-agent system
2. **Caching**: Add Redis/database caching for repeated company verifications
3. **Advanced Analysis**: Use AI (Gemini) to analyze search results
4. **Industry Validation**: Cross-reference company with industry databases
5. **Social Media**: Verify LinkedIn, Facebook company pages

### Example: Integrate into Employment Agent

```python
# In agents/employment.py
from serper_service import get_serper_service

class EmploymentAgent:
    def _simulate_linkedin_check(self, employer: str, ...):
        # Replace simulation with real Serper API
        serper = get_serper_service()
        verification = serper.verify_company(employer)
        
        if verification["verified"]:
            return {
                "found": True,
                "profile_url": verification["results"][0]["link"] if verification["results"] else None,
                "confidence": verification["confidence"]
            }
        
        return {"found": False}
```

---

## 📚 Additional Resources

- **Serper.dev Documentation**: [https://serper.dev/docs](https://serper.dev/docs)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Pydantic Models**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)

---

## 🤝 Support

For issues or questions:

1. Check the test script: `python test_simple_endpoint.py`
2. View API docs: `http://localhost:8000/docs`
3. Check server logs: `tail -f server.log`
4. Review this documentation

---

**Built with ❤️ using FastAPI, Serper.dev API, and Python**
