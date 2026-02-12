"""
Credit History Agent - Deterministic credit evaluation.
Calculates credit risk based on financial metrics.
"""

import logging
from models import CreditResult, RiskCategory, LoanApplicationRequest

logger = logging.getLogger(__name__)


class CreditAgent:
    """
    Credit History Agent performs deterministic credit analysis.
    Evaluates creditworthiness based on income, loans, and repayment history.
    """
    
    # Risk thresholds
    LOW_RISK_THRESHOLD = 0.3
    MEDIUM_RISK_THRESHOLD = 0.6
    
    def __init__(self):
        self.agent_name = "CreditAgent"
        logger.info(f"{self.agent_name} initialized")
    
    async def process(self, application: LoanApplicationRequest) -> CreditResult:
        """
        Evaluate credit risk for loan application.
        
        Args:
            application: Loan application request
            
        Returns:
            CreditResult with risk assessment
        """
        try:
            logger.info(f"{self.agent_name} evaluating credit for {application.name}")
            
            # Calculate financial ratios
            debt_to_income = self._calculate_debt_to_income(application)
            loan_to_income = self._calculate_loan_to_income(application)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                application, debt_to_income, loan_to_income
            )
            
            # Determine risk category
            risk_category = self._determine_risk_category(risk_score)
            
            # Calculate normalized credit score (0-10)
            credit_score = self._calculate_credit_score(application)
            
            # Determine approval
            approved = risk_score < self.MEDIUM_RISK_THRESHOLD
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                application, debt_to_income, loan_to_income, 
                risk_score, risk_category, credit_score
            )
            
            result = CreditResult(
                risk_category=risk_category,
                risk_score=round(risk_score, 3),
                debt_to_income_ratio=round(debt_to_income, 3),
                loan_to_income_ratio=round(loan_to_income, 3),
                credit_score=round(credit_score, 2),
                reasoning=reasoning,
                approved=approved
            )
            
            logger.info(f"{self.agent_name} completed: {risk_category.value} risk, score={risk_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _calculate_debt_to_income(self, application: LoanApplicationRequest) -> float:
        """
        Calculate debt-to-income ratio.
        Assumes average existing loan of $10,000 per loan.
        
        Args:
            application: Loan application request
            
        Returns:
            Debt-to-income ratio
        """
        # Estimate monthly debt payment (assume 5% monthly payment of total debt)
        estimated_existing_debt = application.existing_loans * 10000
        monthly_debt = estimated_existing_debt * 0.05
        monthly_income = application.income / 12
        
        return monthly_debt / monthly_income if monthly_income > 0 else 0
    
    def _calculate_loan_to_income(self, application: LoanApplicationRequest) -> float:
        """
        Calculate loan-to-income ratio.
        
        Args:
            application: Loan application request
            
        Returns:
            Loan-to-income ratio
        """
        return application.loan_amount / application.income if application.income > 0 else 0
    
    def _calculate_credit_score(self, application: LoanApplicationRequest) -> float:
        """
        Calculate normalized credit score (0-10 scale).
        
        Args:
            application: Loan application request
            
        Returns:
            Credit score
        """
        # Repayment score is already on 0-10 scale
        repayment_component = application.repayment_score
        
        # Penalty for existing loans (up to -3 points)
        loan_penalty = min(application.existing_loans * 0.5, 3.0)
        
        # Bonus for high income relative to loan (up to +1 point)
        income_bonus = min((application.income / application.loan_amount) * 0.2, 1.0)
        
        credit_score = repayment_component - loan_penalty + income_bonus
        
        # Clamp to 0-10 range
        return max(0, min(10, credit_score))
    
    def _calculate_risk_score(
        self, 
        application: LoanApplicationRequest,
        debt_to_income: float,
        loan_to_income: float
    ) -> float:
        """
        Calculate overall risk score (0-1 scale, higher = riskier).
        
        Args:
            application: Loan application request
            debt_to_income: Debt-to-income ratio
            loan_to_income: Loan-to-income ratio
            
        Returns:
            Risk score (0-1)
        """
        # Weight different factors
        weights = {
            'debt_to_income': 0.25,
            'loan_to_income': 0.25,
            'existing_loans': 0.20,
            'repayment_history': 0.30
        }
        
        # Normalize debt-to-income (0.5+ is very high)
        dti_risk = min(debt_to_income / 0.5, 1.0)
        
        # Normalize loan-to-income (2.0+ is very high)
        lti_risk = min(loan_to_income / 2.0, 1.0)
        
        # Normalize existing loans (4+ is high)
        existing_loans_risk = min(application.existing_loans / 4.0, 1.0)
        
        # Normalize repayment score (inverted, 0=worst, 10=best)
        repayment_risk = 1.0 - (application.repayment_score / 10.0)
        
        # Calculate weighted risk score
        risk_score = (
            dti_risk * weights['debt_to_income'] +
            lti_risk * weights['loan_to_income'] +
            existing_loans_risk * weights['existing_loans'] +
            repayment_risk * weights['repayment_history']
        )
        
        return max(0, min(1, risk_score))
    
    def _determine_risk_category(self, risk_score: float) -> RiskCategory:
        """
        Determine risk category from score.
        
        Args:
            risk_score: Risk score (0-1)
            
        Returns:
            RiskCategory enum
        """
        if risk_score < self.LOW_RISK_THRESHOLD:
            return RiskCategory.LOW
        elif risk_score < self.MEDIUM_RISK_THRESHOLD:
            return RiskCategory.MEDIUM
        else:
            return RiskCategory.HIGH
    
    def _generate_reasoning(
        self,
        application: LoanApplicationRequest,
        debt_to_income: float,
        loan_to_income: float,
        risk_score: float,
        risk_category: RiskCategory,
        credit_score: float
    ) -> str:
        """
        Generate detailed reasoning for credit assessment.
        
        Args:
            application: Loan application request
            debt_to_income: Debt-to-income ratio
            loan_to_income: Loan-to-income ratio
            risk_score: Calculated risk score
            risk_category: Risk category
            credit_score: Credit score
            
        Returns:
            Reasoning string
        """
        lines = [
            f"Credit Assessment for {application.name}:",
            f"• Credit Score: {credit_score:.2f}/10",
            f"• Overall Risk: {risk_category.value} ({risk_score:.3f})",
            f"• Debt-to-Income Ratio: {debt_to_income:.2%}",
            f"• Loan-to-Income Ratio: {loan_to_income:.2f}x",
            f"• Existing Loans: {application.existing_loans}",
            f"• Repayment History Score: {application.repayment_score}/10",
            ""
        ]
        
        # Add specific observations
        if debt_to_income < 0.3:
            lines.append("✓ Excellent debt-to-income ratio")
        elif debt_to_income < 0.5:
            lines.append("⚠ Moderate debt-to-income ratio")
        else:
            lines.append("✗ High debt-to-income ratio - concerning")
        
        if loan_to_income < 1.0:
            lines.append("✓ Loan amount is reasonable relative to income")
        elif loan_to_income < 2.0:
            lines.append("⚠ Loan amount is significant relative to income")
        else:
            lines.append("✗ Loan amount is very high relative to income")
        
        if application.repayment_score >= 8.0:
            lines.append("✓ Excellent repayment history")
        elif application.repayment_score >= 6.0:
            lines.append("⚠ Acceptable repayment history")
        else:
            lines.append("✗ Poor repayment history")
        
        if application.existing_loans == 0:
            lines.append("✓ No existing loan burden")
        elif application.existing_loans <= 2:
            lines.append("⚠ Some existing loan obligations")
        else:
            lines.append("✗ Multiple existing loans")
        
        return "\n".join(lines)
