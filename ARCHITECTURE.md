# Project Architecture Overview

## Agentic AI Loan Eligibility Verification System

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│                        (main.py)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Orchestrator Agent   │◄──── Database (SQLite)
         │   (orchestrator.py)   │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │Greeting│  │ Planner │  │  Credit  │
   │ Agent  │  │  Agent  │  │  Agent   │
   └────────┘  └─────────┘  └──────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Employment   │ │Collateral│ │   Critique   │
│    Agent     │ │  Agent   │ │    Agent     │
└──────────────┘ └──────────┘ └──────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Final Decision  │
            │     Agent       │
            └─────────────────┘
```

## File Structure

```
/home/labuser/Loan verification/
│
├── main.py                      # FastAPI application entry point
├── models.py                    # Pydantic models for data validation
├── database.py                  # SQLite database operations
├── orchestrator.py              # Main orchestrator agent
│
├── agents/                      # Agent modules
│   ├── __init__.py
│   ├── greeting.py             # Initial greeting agent
│   ├── planner.py              # Task planning agent
│   ├── credit.py               # Credit verification (deterministic)
│   ├── employment.py           # Employment verification (simulated)
│   ├── collateral.py           # Collateral assessment
│   ├── critique.py             # Quality review (AI-powered)
│   └── final_decision.py       # Final decision (AI-powered)
│
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variable template
├── .env                        # Your environment variables (create this)
├── .gitignore                  # Git ignore rules
│
├── README.md                   # Comprehensive documentation
├── ARCHITECTURE.md             # This file
├── setup.sh                    # Quick setup script
└── test_system.py              # Test script with sample applications
```

## Agent Responsibilities

### 1. Orchestrator Agent (orchestrator.py)
**Purpose**: Coordinates all verification agents and manages workflow

**Responsibilities**:
- Receives loan application from API
- Creates and manages task in database
- Executes agents in proper sequence
- Aggregates results from all agents
- Returns final response to API

**Workflow**:
1. Create task (PENDING)
2. Mark as IN_PROGRESS
3. Execute Greeting Agent
4. Execute Planner Agent
5. Execute verification agents in parallel (Credit, Employment, Collateral)
6. Execute Critique Agent
7. Execute Final Decision Agent
8. Store results and mark COMPLETED

---

### 2. Greeting Agent (agents/greeting.py)
**Purpose**: Send initial acknowledgement to applicant

**Logic**: Deterministic (template-based)

**Outputs**:
- Personalized greeting message
- Application receipt confirmation
- Timestamp

**No external dependencies**

---

### 3. Planner Agent (agents/planner.py)
**Purpose**: Break down verification into subtasks

**Logic**: Rule-based planning

**Outputs**:
- List of verification tasks
- Execution order
- Estimated duration

**Considers**:
- Number of existing loans (enhanced debt analysis)
- Employment duration (enhanced employment check)
- Loan-to-income ratio (high amount review)

---

### 4. Credit History Agent (agents/credit.py)
**Purpose**: Calculate credit risk using deterministic logic

**Logic**: Fully deterministic - NO AI

**Inputs**:
- Income
- Loan amount
- Existing loans
- Repayment score (0-10)

**Calculations**:
- Debt-to-Income (DTI) ratio
- Loan-to-Income (LTI) ratio
- Credit score (0-10 scale)
- Risk score (0-1 scale)

**Risk Categories**:
- Low: risk_score < 0.3
- Medium: 0.3 ≤ risk_score < 0.6
- High: risk_score ≥ 0.6

**Weightings**:
- DTI ratio: 25%
- LTI ratio: 25%
- Existing loans: 20%
- Repayment history: 30%

---

### 5. Employment Verification Agent (agents/employment.py)
**Purpose**: Verify employment and company legitimacy

**Logic**: Simulated web searches (NO actual scraping)

**Simulated Checks**:
1. **LinkedIn Profile Check**: Based on employment years
2. **Glassdoor Company Check**: Based on company name

**Known Reputable Companies** (hardcoded list):
- Tech: Google, Microsoft, Apple, Amazon, Meta, etc.
- Finance: Goldman Sachs, JPMorgan, etc.
- Pharma: Pfizer, Johnson & Johnson, etc.

**Stability Assessment**:
- Excellent: 5+ years at verified company
- Good: 3-5 years at verified company
- Fair: 1-3 years
- Poor: < 1 year

**Risk Flags**:
- Employment not verified
- Company not verified
- Employment < 1 year

---

### 6. Collateral Verification Agent (agents/collateral.py)
**Purpose**: Assess collateral value and LTV ratio

**Logic**: Deterministic financial calculations

**Key Metrics**:
- **LTV Ratio**: Loan / Collateral Value
- **Coverage**: Collateral Value / Loan
- **Standard LTV Threshold**: 80%

**Adequacy Criteria**:
- LTV ≤ 80% AND
- Coverage ≥ 125% (1/0.8)

**Margin Assessment**:
- Excellent: LTV ≤ 60%
- Good: LTV ≤ 70%
- Acceptable: LTV ≤ 80%
- Marginal: LTV 80-90%
- Insufficient: LTV 90-100%
- Inadequate: LTV > 100%

---

### 7. Critique Agent (agents/critique.py)
**Purpose**: Review all verification results for consistency

**Logic**: AI-powered (Gemini) + rule-based fallback

**With AI (Gemini API)**:
- Analyzes all verification results
- Identifies inconsistencies
- Provides holistic assessment
- Generates recommendations

**Without AI (fallback)**:
- Rule-based consistency checks
- Issue identification
- Confidence scoring

**Checks**:
- Alignment of approvals across agents
- Risk signal consistency
- Cross-verification validation

**Outputs**:
- Consistency check summary
- List of identified issues
- Recommendations
- Overall assessment
- Confidence score (0-1)

---

### 8. Final Decision Agent (agents/final_decision.py)
**Purpose**: Make ultimate loan decision

**Logic**: AI-powered (Gemini) + rule-based fallback

**Decision Options**:
1. **APPROVED**: Low risk, all checks passed
2. **CONDITIONAL**: Medium risk, conditions required
3. **REJECTED**: High risk or critical failures

**Decision Logic**:
```
Risk Score < 0.3 + All checks passed → APPROVED
Risk Score < 0.5 + 2+ checks passed → CONDITIONAL
Risk Score < 0.6 + 1+ check passed → CONDITIONAL
Otherwise → REJECTED
```

**Overall Risk Calculation**:
- Credit risk: 45% weight
- Employment risk: 25% weight
- Collateral risk: 30% weight

**Conditions Generated For**:
- Credit concerns → Co-signer, credit reports
- Employment concerns → Pay stubs, verification letter
- Collateral concerns → Increased down payment, appraisal
- High debt → Debt reduction required

**AI Enhancement**:
- Comprehensive reasoning
- Contextual explanation
- Professional language
- Actionable insights

---

## Data Flow

### Request Flow
```
Client Request (JSON)
    ↓
FastAPI Endpoint (/loan/apply)
    ↓
Pydantic Validation (models.py)
    ↓
Orchestrator Agent
    ↓
Database (Create Task - PENDING)
    ↓
Greeting Agent → Result 1
    ↓
Planner Agent → Result 2
    ↓
[Parallel Execution]
    ├─→ Credit Agent → Result 3
    ├─→ Employment Agent → Result 4
    └─→ Collateral Agent → Result 5
    ↓
Critique Agent (Reviews 3,4,5) → Result 6
    ↓
Final Decision Agent (Reviews all) → Result 7
    ↓
Database (Update Task - COMPLETED)
    ↓
Response to Client (JSON)
```

### Database Schema
```sql
CREATE TABLE loan_tasks (
    task_id TEXT PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    status TEXT NOT NULL,        -- pending, in_progress, completed, failed
    request_data TEXT NOT NULL,  -- JSON
    result_data TEXT,            -- JSON (when completed)
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## API Endpoints

### POST /loan/apply
Submit loan application for verification

**Request Body**:
```json
{
  "name": "string",
  "income": float,
  "loan_amount": float,
  "existing_loans": int,
  "repayment_score": float (0-10),
  "employment_years": float,
  "company_name": "string",
  "collateral_value": float
}
```

**Response**:
```json
{
  "decision": "Approved|Rejected|Conditional",
  "risk_score": float (0-1),
  "reasoning": "string",
  "agent_summary": {
    "greeting": {...},
    "planner": {...},
    "credit": {...},
    "employment": {...},
    "collateral": {...},
    "critique": {...},
    "final_decision": {...}
  },
  "task_id": "string",
  "processed_at": "ISO timestamp"
}
```

### GET /health
System health check

### GET /loan/task/{task_id}
Get status of specific task

### GET /loan/recent?limit=10
Get recent applications

### GET /stats
Get system statistics

### GET /docs
Interactive API documentation (Swagger UI)

### GET /redoc
Alternative API documentation (ReDoc)

## Environment Configuration

### Required Environment Variables

```bash
# Gemini API Key (optional but recommended)
GEMINI_API_KEY=your_api_key_here

# Database Path (optional, defaults to ./loan_verification.db)
DATABASE_PATH=./loan_verification.db

# Logging Level (optional, defaults to INFO)
LOG_LEVEL=INFO

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
```

### AI Features

**With GEMINI_API_KEY**:
- Critique Agent uses AI for comprehensive review
- Final Decision Agent uses AI for reasoning
- Enhanced, context-aware explanations

**Without GEMINI_API_KEY**:
- System falls back to rule-based logic
- Fully functional but less sophisticated
- Good for testing and development

## Key Design Decisions

### 1. Multi-Agent Architecture
- **Why**: Separation of concerns, modularity, easier testing
- Each agent has single responsibility
- Agents can be updated independently
- Clear workflow and data flow

### 2. Deterministic Credit Analysis
- **Why**: Transparency, explainability, regulatory compliance
- No black-box AI for core financial calculations
- Auditable decision logic
- Consistent results

### 3. Simulated Web Verification
- **Why**: No actual scraping, faster, no rate limits
- Demonstrates concept without legal/technical issues
- Easy to replace with real APIs later
- Controlled testing environment

### 4. Hybrid AI/Rule-Based Approach
- **Why**: Best of both worlds
- AI for reasoning and consistency checks
- Rules for financial calculations
- Fallback logic when AI unavailable

### 5. SQLite Database
- **Why**: Lightweight, no setup, embedded
- Perfect for development and small deployments
- Easy to upgrade to PostgreSQL/MySQL
- Full ACID compliance

### 6. FastAPI Framework
- **Why**: Modern, fast, automatic documentation
- Async support for better performance
- Built-in validation with Pydantic
- Excellent developer experience

## Testing Strategy

### Unit Testing (Recommended)
Test individual agents:
```python
pytest tests/test_credit_agent.py
pytest tests/test_employment_agent.py
# etc.
```

### Integration Testing
Use provided test script:
```bash
python test_system.py
```

### Manual Testing
Use Swagger UI at http://localhost:8000/docs

### Test Scenarios Included

1. **Strong Applicant**: High income, no loans, excellent history
2. **Moderate Applicant**: Medium income, some loans, good history
3. **Weak Applicant**: Low income, many loans, poor history
4. **Mixed Profile**: Good credit but recent employment
5. **Excellent Profile**: Top tier in all categories

## Performance Considerations

### Expected Response Times
- Without AI: 1-3 seconds
- With AI: 3-7 seconds (depends on Gemini API)

### Scalability
- Current design: Single process
- For production: Add async task queue (Celery/RQ)
- Database: Can handle thousands of records
- For high load: Switch to PostgreSQL + connection pooling

### Optimization Opportunities
1. Cache Gemini responses for similar requests
2. Parallel agent execution (already implemented for verification)
3. Database connection pooling
4. Redis for session/cache management
5. Load balancing for multiple instances

## Security Considerations

### Current Implementation
- Input validation via Pydantic
- Environment variable for API keys
- CORS middleware (configure for production)
- Basic error handling

### Production Recommendations
1. Add authentication (OAuth2, JWT)
2. API rate limiting
3. Input sanitization
4. HTTPS/TLS
5. Database encryption at rest
6. Audit logging
7. Role-based access control
8. Secure API key management (vault)

## Extensibility

### Easy to Add
1. New agents (add to agents/ folder)
2. Additional verification checks
3. Different AI models (swap Gemini)
4. Real web scraping (replace simulations)
5. Email notifications
6. Document uploads
7. Multi-language support

### Integration Points
- External credit bureau APIs
- Real employment verification services
- Property valuation APIs
- Email/SMS notification services
- Document management systems

## Troubleshooting

### Common Issues

**Import Errors**
- Solution: Ensure virtual environment is activated
- Run: `source venv/bin/activate`

**Database Locked**
- Solution: Close other connections or delete .db file
- Run: `rm loan_verification.db`

**Gemini API Errors**
- Solution: Check API key in .env file
- System works without AI (uses fallback)

**Port Already in Use**
- Solution: Use different port
- Run: `uvicorn main:app --port 8001`

## Future Enhancements

### Phase 2 Features
- [ ] Real credit bureau integration
- [ ] Actual employment verification APIs
- [ ] Document upload and OCR
- [ ] Email notifications to applicants
- [ ] Admin dashboard
- [ ] Detailed analytics

### Phase 3 Features
- [ ] Machine learning risk models
- [ ] Real-time monitoring
- [ ] Multi-tenant support
- [ ] Mobile application
- [ ] Blockchain audit trail
- [ ] Advanced fraud detection

---

**Version**: 1.0.0  
**Last Updated**: February 11, 2026  
**Author**: AI Agent  
**License**: Educational/Demonstration
