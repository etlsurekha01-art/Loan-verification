"""
Pydantic models for loan verification system.
Defines request/response schemas and data transfer objects.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class RiskCategory(str, Enum):
    """Risk categories for loan applications"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class LoanDecision(str, Enum):
    """Final loan decision options"""
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CONDITIONAL = "Conditional"


class LoanApplicationRequest(BaseModel):
    """
    Loan application request model.
    Contains all necessary information for loan verification.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Applicant full name")
    income: float = Field(..., gt=0, description="Annual income in USD")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount in USD")
    existing_loans: int = Field(..., ge=0, description="Number of existing loans")
    repayment_score: float = Field(..., ge=0, le=10, description="Repayment history score (0-10)")
    employment_years: float = Field(..., ge=0, description="Years of employment at current company")
    company_name: str = Field(..., min_length=2, max_length=100, description="Current employer name")
    collateral_value: float = Field(..., ge=0, description="Collateral value in USD")
    
    # Optional employment verification fields
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    job_title: Optional[str] = Field(None, max_length=100, description="Current job title")
    previous_employers: Optional[int] = Field(None, ge=0, description="Number of previous employers")
    employment_type: Optional[str] = Field(None, description="Employment type (Full-time, Part-time, Contract)")
    professional_email: Optional[str] = Field(None, description="Professional/work email address")

    @validator('income', 'loan_amount', 'collateral_value')
    def validate_positive_amounts(cls, v):
        """Ensure monetary values are positive"""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @validator('repayment_score')
    def validate_repayment_score(cls, v):
        """Ensure repayment score is within valid range"""
        if not 0 <= v <= 10:
            raise ValueError("Repayment score must be between 0 and 10")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "income": 75000.0,
                "loan_amount": 50000.0,
                "existing_loans": 1,
                "repayment_score": 8.5,
                "employment_years": 5.5,
                "company_name": "Tech Corp",
                "collateral_value": 60000.0,
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "job_title": "Senior Software Engineer",
                "previous_employers": 2,
                "employment_type": "Full-time",
                "professional_email": "john.doe@techcorp.com"
            }
        }


class GreetingResult(BaseModel):
    """Result from greeting agent"""
    message: str
    timestamp: str


class PlannerResult(BaseModel):
    """Result from planner agent - task breakdown"""
    tasks: list[str]
    execution_order: list[str]
    estimated_duration: str


class CreditResult(BaseModel):
    """Result from credit history verification"""
    risk_category: RiskCategory
    risk_score: float = Field(..., ge=0, le=1, description="Risk score from 0 (lowest) to 1 (highest)")
    debt_to_income_ratio: float
    loan_to_income_ratio: float
    credit_score: float = Field(..., ge=0, le=10, description="Calculated credit score")
    reasoning: str
    approved: bool


class EmploymentResult(BaseModel):
    """Result from employment verification"""
    employment_verified: bool
    company_verified: bool
    employment_stability: str  # "Excellent", "Good", "Fair", "Poor"
    linkedin_check: str  # Simulated result
    glassdoor_check: str  # Simulated result
    linkedin_profile_found: bool = Field(default=False, description="Whether LinkedIn profile was found")
    profile_completeness: Optional[str] = Field(None, description="LinkedIn profile completeness assessment")
    employment_history_verified: bool = Field(default=False, description="Whether employment history matches")
    professional_credentials: Optional[str] = Field(None, description="Professional credentials assessment")
    reasoning: str
    risk_flag: bool


class CollateralResult(BaseModel):
    """Result from collateral verification"""
    collateral_adequate: bool
    ltv_ratio: float = Field(..., description="Loan-to-Value ratio")
    collateral_coverage: float = Field(..., description="Percentage of loan covered by collateral")
    margin_assessment: str
    reasoning: str
    approved: bool


class CritiqueResult(BaseModel):
    """Result from critique agent - quality review"""
    consistency_check: str
    identified_issues: list[str]
    recommendations: list[str]
    overall_assessment: str
    confidence_score: float = Field(..., ge=0, le=1)


class FinalDecisionResult(BaseModel):
    """Final loan decision result"""
    decision: LoanDecision
    risk_score: float = Field(..., ge=0, le=1)
    reasoning: str
    conditions: Optional[list[str]] = None  # For conditional approvals
    confidence: float = Field(..., ge=0, le=1)


class AgentSummary(BaseModel):
    """Summary of all agent outputs"""
    greeting: Optional[GreetingResult] = None
    planner: Optional[PlannerResult] = None
    credit: Optional[CreditResult] = None
    employment: Optional[EmploymentResult] = None
    collateral: Optional[CollateralResult] = None
    critique: Optional[CritiqueResult] = None
    final_decision: Optional[FinalDecisionResult] = None


class LoanApplicationResponse(BaseModel):
    """
    Final response to loan application.
    Contains decision, risk assessment, and detailed reasoning.
    """
    decision: LoanDecision
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    reasoning: str = Field(..., description="Detailed explanation of the decision")
    agent_summary: AgentSummary
    task_id: Optional[str] = None
    processed_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Approved",
                "risk_score": 0.25,
                "reasoning": "Applicant has strong credit history, stable employment, and adequate collateral coverage.",
                "agent_summary": {
                    "credit": {
                        "risk_category": "Low",
                        "risk_score": 0.2,
                        "approved": True
                    },
                    "employment": {
                        "employment_verified": True,
                        "employment_stability": "Excellent"
                    },
                    "collateral": {
                        "collateral_adequate": True,
                        "ltv_ratio": 0.75
                    }
                },
                "task_id": "task_123456",
                "processed_at": "2026-02-11T10:30:00"
            }
        }


class TaskStatus(str, Enum):
    """Task processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class LoanTask(BaseModel):
    """
    Database model for loan verification task.
    Tracks the state of each loan application.
    """
    task_id: str
    applicant_name: str
    status: TaskStatus
    request_data: Dict[str, Any]
    result_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"
    database_connected: bool
