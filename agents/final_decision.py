"""
Final Decision Agent - Makes the ultimate loan approval decision.
Synthesizes all verification results into a final decision with reasoning.
"""

import logging
import os
from typing import Optional
import google.generativeai as genai

from models import (
    FinalDecisionResult,
    LoanDecision,
    CreditResult,
    EmploymentResult,
    CollateralResult,
    CritiqueResult,
    LoanApplicationRequest
)

logger = logging.getLogger(__name__)


class FinalDecisionAgent:
    """
    Final Decision Agent makes the ultimate loan approval decision.
    Synthesizes all agent outputs into a comprehensive final decision.
    """
    
    def __init__(self):
        self.agent_name = "FinalDecisionAgent"
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
        collateral_result: CollateralResult,
        critique_result: CritiqueResult
    ) -> FinalDecisionResult:
        """
        Make final loan decision based on all verifications.
        
        Args:
            application: Original loan application
            credit_result: Credit verification result
            employment_result: Employment verification result
            collateral_result: Collateral verification result
            critique_result: Critique assessment
            
        Returns:
            FinalDecisionResult with decision and reasoning
        """
        try:
            logger.info(f"{self.agent_name} making decision for {application.name}")
            
            # Calculate overall risk score
            risk_score = self._calculate_overall_risk(
                credit_result,
                employment_result,
                collateral_result
            )
            
            # Make decision
            decision = self._make_decision(
                credit_result,
                employment_result,
                collateral_result,
                risk_score
            )
            
            # Generate conditions for conditional approvals
            conditions = self._generate_conditions(
                decision,
                credit_result,
                employment_result,
                collateral_result,
                critique_result
            )
            
            # Generate comprehensive reasoning
            if self.model:
                reasoning = await self._ai_reasoning(
                    application,
                    credit_result,
                    employment_result,
                    collateral_result,
                    critique_result,
                    decision,
                    risk_score
                )
            else:
                reasoning = self._fallback_reasoning(
                    application,
                    credit_result,
                    employment_result,
                    collateral_result,
                    decision,
                    risk_score
                )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                credit_result,
                employment_result,
                collateral_result,
                critique_result,
                decision
            )
            
            result = FinalDecisionResult(
                decision=decision,
                risk_score=round(risk_score, 3),
                reasoning=reasoning,
                conditions=conditions if conditions else None,
                confidence=round(confidence, 3)
            )
            
            logger.info(f"{self.agent_name} decision: {decision.value}, risk={risk_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _calculate_overall_risk(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult
    ) -> float:
        """
        Calculate overall risk score from all verifications.
        
        Returns:
            Overall risk score (0-1)
        """
        # Weighted combination of risk factors
        weights = {
            'credit': 0.45,          # Credit is most important
            'employment': 0.25,      # Employment stability
            'collateral': 0.30       # Collateral coverage
        }
        
        # Credit risk (already 0-1)
        credit_risk = credit.risk_score
        
        # Employment risk (convert to 0-1)
        employment_risk = 0.0
        if employment.risk_flag:
            employment_risk += 0.5
        if not employment.employment_verified:
            employment_risk += 0.3
        if employment.employment_stability == "Poor":
            employment_risk += 0.2
        employment_risk = min(employment_risk, 1.0)
        
        # Collateral risk (convert to 0-1)
        collateral_risk = min(collateral.ltv_ratio / 0.80, 1.0)
        if not collateral.collateral_adequate:
            collateral_risk = max(collateral_risk, 0.7)
        
        # Calculate weighted risk
        overall_risk = (
            credit_risk * weights['credit'] +
            employment_risk * weights['employment'] +
            collateral_risk * weights['collateral']
        )
        
        return max(0.0, min(1.0, overall_risk))
    
    def _make_decision(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        risk_score: float
    ) -> LoanDecision:
        """
        Make loan decision based on verification results.
        
        Returns:
            LoanDecision enum
        """
        # Count approvals
        approvals = [
            credit.approved,
            not employment.risk_flag,
            collateral.approved
        ]
        approval_count = sum(approvals)
        
        # Decision logic
        if risk_score < 0.3 and approval_count == 3:
            # Low risk, all checks passed
            return LoanDecision.APPROVED
        
        elif risk_score < 0.5 and approval_count >= 2:
            # Medium-low risk, most checks passed
            if credit.approved and collateral.approved:
                # Core financial checks passed, can work with employment concerns
                return LoanDecision.CONDITIONAL
            elif credit.approved and not employment.risk_flag:
                # Good credit and employment, collateral needs work
                return LoanDecision.CONDITIONAL
            else:
                return LoanDecision.CONDITIONAL
        
        elif risk_score < 0.6 and approval_count >= 1:
            # Medium-high risk, some checks passed
            return LoanDecision.CONDITIONAL
        
        else:
            # High risk or too many failures
            return LoanDecision.REJECTED
    
    def _generate_conditions(
        self,
        decision: LoanDecision,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        critique: CritiqueResult
    ) -> Optional[list[str]]:
        """
        Generate conditions for conditional approvals.
        
        Returns:
            List of conditions or None
        """
        if decision != LoanDecision.CONDITIONAL:
            return None
        
        conditions = []
        
        # Credit-based conditions
        if not credit.approved or credit.risk_score > 0.4:
            conditions.append("Provide co-signer with good credit standing")
            conditions.append("Submit detailed credit report from all three bureaus")
        
        # Employment conditions
        if employment.risk_flag or not employment.employment_verified:
            conditions.append("Provide three recent pay stubs")
            conditions.append("Submit employment verification letter from HR")
        
        if employment.employment_stability in ["Fair", "Poor"]:
            conditions.append("Provide proof of income continuity for 6 months")
        
        # Collateral conditions
        if not collateral.approved or collateral.ltv_ratio > 0.75:
            conditions.append("Increase down payment to achieve LTV ≤ 75%")
            conditions.append("Provide professional collateral appraisal")
        
        # General conditions
        if credit.debt_to_income_ratio > 0.4:
            conditions.append("Reduce existing debt obligations")
        
        # Use critique recommendations
        if critique.recommendations:
            for rec in critique.recommendations[:2]:  # Add top 2 recommendations
                if "Request" in rec or "Consider" in rec or "require" in rec.lower():
                    conditions.append(rec)
        
        return conditions if conditions else ["Standard loan conditions apply"]
    
    async def _ai_reasoning(
        self,
        application: LoanApplicationRequest,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        critique: CritiqueResult,
        decision: LoanDecision,
        risk_score: float
    ) -> str:
        """
        Generate AI-powered decision reasoning.
        
        Returns:
            Reasoning string
        """
        try:
            prompt = f"""
You are a senior loan officer making a final loan decision. Provide clear, professional reasoning for the decision.

Applicant: {application.name}
Loan Amount Requested: ${application.loan_amount:,.2f}
Annual Income: ${application.income:,.2f}

VERIFICATION RESULTS:

Credit Analysis:
- Risk: {credit.risk_category.value} ({credit.risk_score:.3f})
- Credit Score: {credit.credit_score}/10
- DTI: {credit.debt_to_income_ratio:.1%}
- Status: {'Approved' if credit.approved else 'Not Approved'}

Employment Verification:
- Verified: {employment.employment_verified}
- Company: {application.company_name} (verified: {employment.company_verified})
- Duration: {application.employment_years} years
- Stability: {employment.employment_stability}

Collateral Assessment:
- LTV Ratio: {collateral.ltv_ratio:.1%}
- Coverage: {collateral.collateral_coverage:.1%}
- Status: {'Adequate' if collateral.collateral_adequate else 'Inadequate'}

Overall Risk Score: {risk_score:.3f}

Critique Summary:
{critique.overall_assessment}

FINAL DECISION: {decision.value.upper()}

Provide a comprehensive but concise explanation (3-4 sentences) that:
1. States the decision clearly
2. Explains the key factors that led to this decision
3. Highlights the most important strengths or concerns
4. For conditional/rejected applications, indicates what would need to change

Be professional, specific, and factual.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI reasoning error: {e}")
            return self._fallback_reasoning(
                application, credit, employment, collateral, decision, risk_score
            )
    
    def _fallback_reasoning(
        self,
        application: LoanApplicationRequest,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        decision: LoanDecision,
        risk_score: float
    ) -> str:
        """
        Generate rule-based reasoning when AI is not available.
        
        Returns:
            Reasoning string
        """
        lines = [
            f"LOAN DECISION: {decision.value.upper()}",
            f"Overall Risk Score: {risk_score:.3f} ({'Low' if risk_score < 0.3 else 'Medium' if risk_score < 0.6 else 'High'} Risk)",
            ""
        ]
        
        if decision == LoanDecision.APPROVED:
            lines.append(
                f"Loan application for {application.name} has been APPROVED for ${application.loan_amount:,.2f}. "
                f"The applicant demonstrates strong creditworthiness with a {credit.risk_category.value.lower()} risk profile "
                f"(credit score: {credit.credit_score:.1f}/10), {employment.employment_stability.lower()} employment stability "
                f"at {application.company_name}, and adequate collateral coverage ({collateral.collateral_coverage:.1%}). "
                f"All key verification checks passed successfully, indicating a low-risk lending opportunity."
            )
        
        elif decision == LoanDecision.CONDITIONAL:
            lines.append(
                f"Loan application for {application.name} has received CONDITIONAL APPROVAL for ${application.loan_amount:,.2f}. "
                f"While the application shows promise with {credit.risk_category.value.lower()} credit risk and "
                f"{employment.employment_stability.lower()} employment stability, certain conditions must be met to proceed. "
            )
            
            concerns = []
            if not credit.approved:
                concerns.append("credit risk mitigation")
            if employment.risk_flag:
                concerns.append("employment verification")
            if not collateral.approved:
                concerns.append("collateral enhancement")
            
            if concerns:
                lines.append(f"Primary areas requiring attention: {', '.join(concerns)}. ")
            
            lines.append(
                "Upon satisfaction of the specified conditions, the loan can proceed to final approval."
            )
        
        else:  # REJECTED
            lines.append(
                f"Loan application for {application.name} has been REJECTED. "
                f"The application presents high risk (score: {risk_score:.3f}) with significant concerns identified "
                f"across multiple verification areas. "
            )
            
            issues = []
            if not credit.approved:
                issues.append(f"{credit.risk_category.value} credit risk")
            if employment.risk_flag:
                issues.append("employment verification concerns")
            if not collateral.approved:
                issues.append("insufficient collateral")
            
            if issues:
                lines.append(f"Key issues: {', '.join(issues)}. ")
            
            lines.append(
                "We recommend the applicant address these concerns and reapply when their financial situation improves."
            )
        
        return "\n".join(lines)
    
    def _calculate_confidence(
        self,
        credit: CreditResult,
        employment: EmploymentResult,
        collateral: CollateralResult,
        critique: CritiqueResult,
        decision: LoanDecision
    ) -> float:
        """
        Calculate confidence in the decision.
        
        Returns:
            Confidence score (0-1)
        """
        # Start with critique confidence
        confidence = critique.confidence_score
        
        # Boost confidence for clear-cut cases
        if decision == LoanDecision.APPROVED:
            if credit.approved and not employment.risk_flag and collateral.approved:
                confidence = min(confidence + 0.15, 1.0)
        
        elif decision == LoanDecision.REJECTED:
            if not credit.approved and employment.risk_flag and not collateral.approved:
                confidence = min(confidence + 0.15, 1.0)
        
        # Conditional approvals have inherently lower confidence
        if decision == LoanDecision.CONDITIONAL:
            confidence = min(confidence, 0.85)
        
        return max(0.0, min(1.0, confidence))
