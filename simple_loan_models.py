"""
Simple models for the check-loan-eligibility endpoint.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SimpleLoanRequest(BaseModel):
    """Simple loan eligibility request"""
    name: str = Field(..., min_length=1, description="Applicant name")
    income: float = Field(..., gt=0, description="Annual income")
    company: str = Field(..., min_length=1, description="Company name")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "income": 75000,
                "company": "Google Inc",
                "loan_amount": 50000,
                "credit_score": 720
            }
        }


class VerificationResult(BaseModel):
    """Single verification result from search"""
    title: str
    snippet: str
    link: str


class SimpleLoanResponse(BaseModel):
    """Simple loan eligibility response"""
    status: str = Field(..., description="APPROVED or REJECTED")
    reason: str = Field(..., description="Reason for decision")
    verification_results: List[VerificationResult] = Field(default=[], description="Search results from company verification")
    company_verified: Optional[bool] = Field(None, description="Whether company was verified")
    verification_confidence: Optional[str] = Field(None, description="Confidence level of verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "APPROVED",
                "reason": "Credit score is 720, income meets requirements ($75000), and company Google Inc has been verified as legitimate.",
                "verification_results": [
                    {
                        "title": "Google Inc - Official Website",
                        "snippet": "Google is a multinational technology company...",
                        "link": "https://www.google.com"
                    }
                ],
                "company_verified": True,
                "verification_confidence": "high"
            }
        }
