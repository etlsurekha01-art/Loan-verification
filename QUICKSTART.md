# 🎯 Quick Start Guide

## Agentic AI Loan Eligibility Verification System

### 📋 What You Have

A production-ready multi-agent loan verification system with:

✅ **8 Specialized Agents** working together  
✅ **FastAPI REST API** with automatic documentation  
✅ **SQLite Database** for task persistence  
✅ **AI Integration** (Google Gemini) with fallback logic  
✅ **Comprehensive Logging** and error handling  
✅ **Test Suite** with multiple scenarios  

---

## 🚀 Installation (3 Steps)

### Option 1: Automated Setup (Recommended)

```bash
cd "/home/labuser/Loan verification"
./setup.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

---

## 🔑 Getting Your Gemini API Key (Optional but Recommended)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy to `.env` file:

```bash
GEMINI_API_KEY=your_actual_key_here
```

**Note**: System works without API key (uses fallback logic), but AI features will be limited.

---

## ▶️ Running the System

### Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --reload
```

Server will be available at: **http://localhost:8000**

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Beautiful documentation)

---

## 🧪 Testing the System

### Run Automated Tests

```bash
# In a new terminal window
source venv/bin/activate
python test_system.py
```

This will run 5 test scenarios:
1. ✅ Strong Applicant (should be APPROVED)
2. ⚠️ Moderate Applicant (should be CONDITIONAL)
3. ❌ Weak Applicant (should be REJECTED)
4. ⚠️ Good Credit, Poor Employment (should be CONDITIONAL)
5. ✅ Excellent Profile (should be APPROVED)

### Manual Testing via API

#### Using cURL:

```bash
curl -X POST "http://localhost:8000/loan/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "income": 75000.0,
    "loan_amount": 50000.0,
    "existing_loans": 1,
    "repayment_score": 8.5,
    "employment_years": 5.5,
    "company_name": "Tech Corp",
    "collateral_value": 60000.0
  }'
```

#### Using Swagger UI:

1. Go to http://localhost:8000/docs
2. Click on `POST /loan/apply`
3. Click "Try it out"
4. Modify the example JSON
5. Click "Execute"

---

## 📁 Project Structure

```
/home/labuser/Loan verification/
│
├── main.py                    # FastAPI application
├── orchestrator.py            # Main coordinator
├── models.py                  # Data models
├── database.py                # SQLite operations
│
├── agents/                    # Agent modules
│   ├── greeting.py           # Initial greeting
│   ├── planner.py            # Task planning
│   ├── credit.py             # Credit analysis (deterministic)
│   ├── employment.py         # Employment verification
│   ├── collateral.py         # Collateral assessment
│   ├── critique.py           # Quality review (AI)
│   └── final_decision.py     # Final decision (AI)
│
├── requirements.txt           # Dependencies
├── .env                      # Your environment variables
├── README.md                 # Full documentation
├── ARCHITECTURE.md           # Technical architecture
├── QUICKSTART.md             # This file
│
├── setup.sh                  # Automated setup
├── test_system.py            # Test suite
└── check_env.py              # Environment verification
```

---

## 🔍 Verify Your Setup

```bash
python check_env.py
```

This checks:
- ✓ Python version (3.9+)
- ✓ All dependencies installed
- ✓ All files present
- ✓ Environment configured

---

## 📊 Understanding the Output

### Sample Response:

```json
{
  "decision": "Approved",
  "risk_score": 0.245,
  "reasoning": "Applicant demonstrates strong creditworthiness...",
  "agent_summary": {
    "credit": {
      "risk_category": "Low",
      "risk_score": 0.2,
      "credit_score": 8.5,
      "approved": true
    },
    "employment": {
      "employment_verified": true,
      "company_verified": true,
      "employment_stability": "Excellent"
    },
    "collateral": {
      "collateral_adequate": true,
      "ltv_ratio": 0.75,
      "approved": true
    },
    "critique": {
      "confidence_score": 0.89
    },
    "final_decision": {
      "decision": "Approved",
      "confidence": 0.91
    }
  },
  "task_id": "task_abc123",
  "processed_at": "2026-02-11T10:30:00"
}
```

### Decision Types:

- **Approved**: Low risk, all checks passed
- **Conditional**: Medium risk, conditions must be met
- **Rejected**: High risk or critical failures

### Risk Score:
- **0.0 - 0.3**: Low Risk
- **0.3 - 0.6**: Medium Risk
- **0.6 - 1.0**: High Risk

---

## 🎮 Sample Test Cases

### 1. Strong Applicant (Should Approve)

```json
{
  "name": "Alice Johnson",
  "income": 100000.0,
  "loan_amount": 30000.0,
  "existing_loans": 0,
  "repayment_score": 9.5,
  "employment_years": 10.0,
  "company_name": "Microsoft",
  "collateral_value": 50000.0
}
```

### 2. Risky Applicant (Should Reject)

```json
{
  "name": "Bob Wilson",
  "income": 30000.0,
  "loan_amount": 50000.0,
  "existing_loans": 4,
  "repayment_score": 3.0,
  "employment_years": 0.5,
  "company_name": "Unknown Co",
  "collateral_value": 10000.0
}
```

### 3. Moderate Applicant (Should be Conditional)

```json
{
  "name": "Carol Smith",
  "income": 60000.0,
  "loan_amount": 40000.0,
  "existing_loans": 2,
  "repayment_score": 7.0,
  "employment_years": 3.0,
  "company_name": "Local Business",
  "collateral_value": 45000.0
}
```

---

## 🛠️ Troubleshooting

### Issue: Port Already in Use

```bash
# Use a different port
uvicorn main:app --port 8001
```

### Issue: Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database Locked

```bash
# Delete and recreate database
rm loan_verification.db
# Restart the server
```

### Issue: API Key Errors

The system will work without a Gemini API key, but with limited AI features:
- Critique Agent uses rule-based logic
- Final Decision Agent uses template-based reasoning

To fix: Add valid API key to `.env` file

---

## 📚 Additional Resources

### API Endpoints:

- `POST /loan/apply` - Submit loan application
- `GET /health` - System health check
- `GET /loan/task/{task_id}` - Get task status
- `GET /loan/recent` - Recent applications
- `GET /stats` - System statistics
- `GET /docs` - Interactive documentation

### Documentation Files:

- **README.md** - Comprehensive documentation
- **ARCHITECTURE.md** - Technical architecture details
- **This file** - Quick start guide

---

## 🎓 How It Works

### Workflow:

```
1. Client submits loan application via API
2. Orchestrator creates task in database
3. Greeting Agent sends acknowledgement
4. Planner Agent breaks down verification tasks
5. Verification Agents work in parallel:
   - Credit Agent: Analyzes financial risk
   - Employment Agent: Verifies job/company
   - Collateral Agent: Assesses collateral
6. Critique Agent reviews all results
7. Final Decision Agent makes decision
8. Response returned to client with full details
```

### Agent Roles:

- 🎯 **Orchestrator**: Coordinates everything
- 👋 **Greeting**: Welcomes applicant
- 📋 **Planner**: Creates verification plan
- 💳 **Credit**: Calculates financial risk (deterministic)
- 💼 **Employment**: Verifies job (simulated web search)
- 🏠 **Collateral**: Assesses loan coverage
- 🔍 **Critique**: Quality control (AI-powered)
- ⚖️ **Final Decision**: Makes decision (AI-powered)

---

## 🌟 Key Features

### ✅ Production Ready
- Comprehensive error handling
- Full logging
- Request validation
- Database persistence

### ✅ Multi-Agent Architecture
- Modular design
- Easy to extend
- Clear separation of concerns
- Independent agent testing

### ✅ AI-Enhanced
- Google Gemini integration
- Intelligent critique
- Context-aware reasoning
- Fallback to rules when needed

### ✅ Deterministic Credit Analysis
- Transparent calculations
- Auditable decisions
- No black-box AI for core risk
- Regulatory-friendly

### ✅ Well Documented
- Inline code comments
- API documentation
- Architecture guide
- Quick start guide

---

## 🚀 Next Steps

1. ✅ **Run the system** - Follow installation steps above
2. ✅ **Test it** - Run test_system.py
3. ✅ **Explore API** - Visit /docs endpoint
4. ✅ **Read architecture** - Check ARCHITECTURE.md
5. ✅ **Customize** - Modify agents for your needs

---

## 💡 Tips

- **Development**: Use `--reload` flag for auto-restart
- **Production**: Remove `--reload`, set proper HOST/PORT
- **Testing**: Use Swagger UI for interactive testing
- **Debugging**: Check logs for detailed information
- **Extending**: Add new agents to `agents/` folder

---

## 📞 Need Help?

1. Check **README.md** for detailed documentation
2. Review **ARCHITECTURE.md** for technical details
3. Run **check_env.py** to verify setup
4. Check server logs for error messages
5. Visit `/docs` for API reference

---

## 🎉 You're Ready!

Your Agentic AI Loan Verification System is complete and ready to use!

**Start the server and visit http://localhost:8000/docs to begin.**

---

*Built with ❤️ using FastAPI, Google Gemini AI, and Python*
