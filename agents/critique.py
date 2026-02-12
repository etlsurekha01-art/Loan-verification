"""
Critique Agent - Reviews and validates outputs from all verification agents.
Uses AI to identify inconsistencies and improve decision quality.
"""

import logging
import os
from typing import Optional
import google.generativeai as genai

from models import (
    CritiqueResult,
    CreditResult,
    EmploymentResult,
    CollateralResult,
    LoanApplicationRequest
)

logger = logging.getLogger(__name__)


class CritiqueAgent:
    """
    Critique Agent performs quality review of all verification results.
    Uses AI to identify inconsistencies and provide additional insights.
    """
    
    def __init__(self):
        self.agent_name = "CritiqueAgent"
        self.model = None
        self._initialize_ai()
        logger.info(f"{self.agent_name} initialized")
    
    def _initialize_ai(self):
        """Initialize Google Gemini AI model"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and api_key != "your_gemini_api_key_here":
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info(f"{self.agent_name} AI model initialized")
            else:
                logger.warning(f"{self.agent_name} running without AI (no valid API key)")
                self.model = None
        except Exception as e:
            logger.error(f"{self.agent_name} AI initialization error: {e}")
            self.model = None
    
    async def process(
        self,
        application: LoanApplicationRequest,
        credit_result: CreditResult,
        employment_result: EmploymentResult,
        collateral_result: CollateralResult
    ) -> CritiqueResult:
        """
        Review and critique all verification results.
        
        Args:
            application: Original loan application
            credit_result: Credit verification result
            employment_result: Employment verification result
            collateral_result: Collateral verification result
            
        Returns:
            CritiqueResult with quality assessment
        """
        try:
            logger.info(f"{self.agent_name} reviewing results for {application.name}")
            
            # Perform consistency checks
            consistency = self._check_consistency(
                credit_result,
                employment_result,
                collateral_result
            )
            
            # Identify specific issues
            issues = self._identify_issues(
                application,
                credit_result,
                employment_result,
                collateral_result
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                application,
                credit_result,
                employment_result,
                collateral_result,
                issues
            )
            
            # Use AI for overall assessment if available
            if self.model:
                overall_assessment = await self._ai_assessment(
                    application,
                    credit_result,
                    employment_result,
                    collateral_result,
                    issues
                )
            else:
                overall_assessment = self._fallback_assessment(
                    credit_result,
                    employment_result,
                    collateral_result
                )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                credit_result,
                employment_result,
                collateral_result,
                issues
            )
            
            result = CritiqueResult(
                consistency_check=consistency,
                identified_issues=issues,
                recommendations=recommendations,
                overall_assessment=overall_assessment,
                confidence_score=round(confidence, 3)
            )
            
            logger.info(f"{self.agent_name} completed: confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _check_consistency(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult
    ) -> str:
        """
        Check consistency across all verifications.
        
        Returns:
            Consistency check summary
        """
        checks = []
        
        # Check if approvals are aligned
        approvals = [credit.approved, not employment.risk_flag, collateral.approved]
        all_pass = all(approvals)
        all_fail = not any(approvals)
        
        if all_pass:
            checks.append("✓ All verification checks passed - consistent positive assessment")
        elif all_fail:
            checks.append("✓ All verification checks failed - consistent negative assessment")
        else:
            checks.append("⚠ Mixed verification results - requires careful review")
        
        # Check risk alignment
        if credit.risk_category.value == "High" and employment.risk_flag:
            checks.append("⚠ Both credit and employment show high risk signals")
        
        if credit.risk_category.value == "Low" and collateral.collateral_adequate:
            checks.append("✓ Strong credit profile backed by adequate collateral")
        
        return "\n".join(checks)
    
    def _identify_issues(
        self,
        application: LoanApplicationRequest,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult
    ) -> list[str]:
        """
        Identify specific issues or concerns.
        
        Returns:
            List of identified issues
        """
        issues = []
        
        # Credit issues
        if credit.risk_score > 0.6:
            issues.append(f"High credit risk score ({credit.risk_score:.2f})")
        
        if credit.debt_to_income_ratio > 0.5:
            issues.append(f"High debt-to-income ratio ({credit.debt_to_income_ratio:.1%})")
        
        if application.repayment_score < 6.0:
            issues.append(f"Poor repayment history (score: {application.repayment_score}/10)")
        
        # Employment issues
        if employment.risk_flag:
            issues.append("Employment verification concerns detected")
        
        if not employment.employment_verified:
            issues.append("Employment could not be verified")
        
        if not employment.company_verified:
            issues.append("Company legitimacy could not be verified")
        
        if application.employment_years < 1.0:
            issues.append(f"Short employment duration ({application.employment_years:.1f} years)")
        
        # Collateral issues
        if not collateral.collateral_adequate:
            issues.append("Insufficient collateral coverage")
        
        if collateral.ltv_ratio > 0.80:
            issues.append(f"High LTV ratio ({collateral.ltv_ratio:.1%})")
        
        # Cross-cutting issues
        if application.loan_amount > application.income * 2:
            issues.append(f"Loan amount significantly exceeds annual income")
        
        if not issues:
            issues.append("No significant issues identified")
        
        return issues
    
    def _generate_recommendations(
        self,
        application: LoanApplicationRequest,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        issues: list[str]
    ) -> list[str]:
        """
        Generate actionable recommendations.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommendations based on issues
        if credit.risk_score > 0.6:
            recommendations.append("Consider requiring a co-signer or guarantor")
        
        if collateral.ltv_ratio > 0.80:
            recommendations.append("Request additional collateral or reduce loan amount")
        
        if employment.risk_flag:
            recommendations.append("Request recent pay stubs and employment verification letter")
        
        if application.employment_years < 2.0:
            recommendations.append("Monitor employment stability closely; consider probationary period")
        
        if credit.debt_to_income_ratio > 0.4:
            recommendations.append("Review detailed debt obligations and repayment capacity")
        
        # Positive recommendations
        if credit.approved and employment.employment_verified and collateral.approved:
            recommendations.append("Strong candidate for standard approval terms")
        
        if credit.risk_category.value == "Low" and collateral.collateral_coverage > 1.5:
            recommendations.append("Consider offering preferential interest rates")
        
        if not recommendations:
            recommendations.append("Proceed with standard underwriting protocols")
        
        return recommendations
    
    async def _ai_assessment(
        self,
        application: LoanApplicationRequest,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        issues: list[str]
    ) -> str:
        """
        Generate AI-powered overall assessment.
        
        Returns:
            Assessment string
        """
        try:
            prompt = f"""
You are a senior loan underwriting expert reviewing a loan application. Provide a concise overall assessment.

Applicant: {application.name}
Loan Amount: ${application.loan_amount:,.2f}
Income: ${application.income:,.2f}

Credit Assessment:
- Risk Category: {credit.risk_category.value}
- Risk Score: {credit.risk_score:.3f}
- Credit Score: {credit.credit_score}/10
- Approved: {credit.approved}

Employment Verification:
- Verified: {employment.employment_verified}
- Company: {application.company_name}
- Years: {application.employment_years}
- Stability: {employment.employment_stability}

Collateral:
- Adequate: {collateral.collateral_adequate}
- LTV: {collateral.ltv_ratio:.1%}
- Coverage: {collateral.collateral_coverage:.1%}

Identified Issues:
{chr(10).join(f"- {issue}" for issue in issues)}

Provide a 2-3 sentence overall assessment focusing on the key factors that should influence the final decision.
Be objective and consider both strengths and weaknesses.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI assessment error: {e}")
            return self._fallback_assessment(credit, employment, collateral)
    
    def _fallback_assessment(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult
    ) -> str:
        """
        Generate rule-based assessment when AI is not available.
        
        Returns:
            Assessment string
        """
        approvals = [credit.approved, not employment.risk_flag, collateral.approved]
        approval_count = sum(approvals)
        
        if approval_count == 3:
            return ("All verification checks passed successfully. The applicant demonstrates strong "
                   "creditworthiness, stable employment, and adequate collateral. Recommended for approval.")
        elif approval_count == 2:
            return ("Most verification checks passed with some concerns noted. The application shows "
                   "acceptable risk levels but may benefit from additional conditions or documentation.")
        elif approval_count == 1:
            return ("Multiple verification concerns identified. The application presents elevated risk "
                   "and would likely require significant conditions or may not meet approval criteria.")
        else:
            return ("Significant concerns across all verification areas. The application presents high risk "
                   "and does not meet standard approval criteria. Rejection recommended.")
    
    def _calculate_confidence(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        issues: list[str]
    ) -> float:
        """
        Calculate confidence score for the assessment.
        
        Returns:
            Confidence score (0-1)
        """
        confidence = 1.0
        
        # Reduce confidence based on verification failures
        if not credit.approved:
            confidence -= 0.15
        
        if employment.risk_flag:
            confidence -= 0.15
        
        if not employment.employment_verified:
            confidence -= 0.10
        
        if not collateral.approved:
            confidence -= 0.15
        
        # Reduce confidence based on number of issues
        issue_penalty = min(len(issues) * 0.05, 0.25)
        confidence -= issue_penalty
        
        # Boost confidence for strong cases
        if credit.approved and not employment.risk_flag and collateral.approved:
            confidence = min(confidence + 0.1, 1.0)
        
        return max(0.0, min(1.0, confidence))
