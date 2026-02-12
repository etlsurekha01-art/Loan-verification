# Agentic AI Loan Eligibility Verification System

A sophisticated multi-agent system for automated loan eligibility verification using Python, FastAPI, and Google Gemini AI.

## Architecture

This system implements a multi-agent architecture with specialized agents working together:

### Agent Components

1. **Orchestrator Agent**: Coordinates all sub-agents and maintains application state
2. **Greeting Agent**: Sends initial acknowledgement to applicants
3. **Planner Agent**: Breaks down verification into subtasks
4. **Credit History Agent**: Evaluates creditworthiness using deterministic logic
5. **Employment Verification Agent**: Validates employment details with simulated web searches
6. **Collateral Verification Agent**: Assesses collateral value and loan-to-value ratio
7. **Critique Agent**: Reviews all agent outputs for consistency
8. **Final Decision Agent**: Makes final approval/rejection decision with reasoning

## Features

- ✅ REST API with FastAPI
- ✅ Multi-agent coordination system
- ✅ SQLite database for task persistence
- ✅ Comprehensive logging
- ✅ Error handling and validation
- ✅ Pydantic models for type safety
- ✅ Modular, production-ready architecture

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /loan/apply

Submit a loan application for verification.

**Request Body**:
```json
{
  "name": "John Doe",
  "income": 75000.0,
  "loan_amount": 50000.0,
  "existing_loans": 1,
  "repayment_score": 8.5,
  "employment_years": 5.5,
  "company_name": "Tech Corp",
  "collateral_value": 60000.0
}
```

**Response**:
```json
{
  "decision": "Approved",
  "risk_score": 0.15,
  "reasoning": "Detailed explanation of the decision",
  "agent_summary": {
    "credit_agent": {...},
    "employment_agent": {...},
    "collateral_agent": {...},
    "critique_agent": {...}
  }
}
```

### GET /health

Health check endpoint.

## Example Usage

### Using cURL:

```bash
curl -X POST "http://localhost:8000/loan/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "income": 90000.0,
    "loan_amount": 40000.0,
    "existing_loans": 0,
    "repayment_score": 9.2,
    "employment_years": 7.0,
    "company_name": "Google Inc",
    "collateral_value": 55000.0
  }'
```

### Using Python:

```python
import requests

url = "http://localhost:8000/loan/apply"
data = {
    "name": "Jane Smith",
    "income": 90000.0,
    "loan_amount": 40000.0,
    "existing_loans": 0,
    "repayment_score": 9.2,
    "employment_years": 7.0,
    "company_name": "Google Inc",
    "collateral_value": 55000.0
}

response = requests.post(url, json=data)
print(response.json())
```

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic models for request/response
├── database.py            # SQLite database operations
├── orchestrator.py        # Main orchestrator agent
├── agents/
│   ├── __init__.py
│   ├── greeting.py        # Greeting agent
│   ├── planner.py         # Planning agent
│   ├── credit.py          # Credit history verification
│   ├── employment.py      # Employment verification
│   ├── collateral.py      # Collateral verification
│   ├── critique.py        # Critique agent
│   └── final_decision.py  # Final decision agent
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Agent Details

### Credit History Agent (Deterministic)
Calculates risk score based on:
- Debt-to-income ratio
- Existing loan burden
- Repayment history (0-10 scale)
- Loan-to-income ratio

**Risk Categories**:
- Low Risk: Score < 0.3
- Medium Risk: Score 0.3 - 0.6
- High Risk: Score > 0.6

### Employment Verification Agent
Simulates verification through:
- LinkedIn profile check (mocked)
- Glassdoor company verification (mocked)
- Employment duration validation
- Company reputation assessment

### Collateral Verification Agent
Evaluates:
- Collateral value vs loan amount
- Loan-to-value (LTV) ratio (80% threshold)
- Collateral adequacy for risk mitigation

### Critique Agent
Uses AI to:
- Review all agent outputs
- Identify inconsistencies
- Provide additional insights
- Improve decision quality

### Final Decision Agent
Makes final determination:
- **Approved**: Low risk, all checks passed
- **Conditional**: Medium risk, additional requirements needed
- **Rejected**: High risk or failed critical checks

## Database Schema

The system uses SQLite with the following schema:

**loan_tasks table**:
- `task_id` (TEXT PRIMARY KEY): Unique task identifier
- `applicant_name` (TEXT): Applicant name
- `status` (TEXT): Task status (pending/completed/failed)
- `request_data` (TEXT): JSON of request data
- `result_data` (TEXT): JSON of verification results
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

## Logging

Logs are output to console with the following levels:
- INFO: General application flow
- WARNING: Non-critical issues
- ERROR: Error conditions
- DEBUG: Detailed debugging information

## Error Handling

The system includes comprehensive error handling:
- Input validation using Pydantic
- Database operation error handling
- API error responses with proper HTTP status codes
- Agent execution error recovery

## Security Considerations

⚠️ **This is a demonstration system**. For production use, consider:
- API authentication (OAuth2, API keys)
- Rate limiting
- Input sanitization
- Secure credential storage
- HTTPS enforcement
- Database encryption
- Audit logging

## Testing

Example test cases to verify functionality:

**High-quality applicant** (should be approved):
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

**Risky applicant** (should be rejected):
```json
{
  "name": "Bob Wilson",
  "income": 30000.0,
  "loan_amount": 50000.0,
  "existing_loans": 3,
  "repayment_score": 4.0,
  "employment_years": 0.5,
  "company_name": "Unknown Startup",
  "collateral_value": 10000.0
}
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Database errors**
   - Delete `loan_verification.db` to reset
   - Check file permissions

3. **API key errors**
   - Verify `.env` file exists
   - Check GEMINI_API_KEY is set correctly
   - Ensure no extra spaces in the key

4. **Port already in use**
   - Change port: `uvicorn main:app --port 8001`

## Future Enhancements

- [ ] Real credit bureau integration
- [ ] Actual web scraping for employment verification
- [ ] Document upload and OCR
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Multi-tenant support
- [ ] Advanced ML risk models
- [ ] Real-time monitoring

## License

This project is for educational and demonstration purposes.

## Contributing

This is a demonstration project. Feel free to fork and enhance!

## Contact

For questions or issues, please open an issue in the repository.

---

Built with ❤️ using FastAPI and Google Gemini AI
