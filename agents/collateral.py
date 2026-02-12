"""
Collateral Verification Agent - Validates collateral value and coverage.
Assesses loan-to-value ratio and collateral adequacy.
"""

import logging
from models import CollateralResult, LoanApplicationRequest

logger = logging.getLogger(__name__)


class CollateralAgent:
    """
    Collateral Verification Agent validates collateral value against loan amount.
    Applies standard lending margins and LTV (Loan-to-Value) ratios.
    """
    
    # Standard LTV threshold (80% is common in lending)
    MAX_LTV_RATIO = 0.80
    
    # Minimum collateral coverage required
    MIN_COVERAGE = 0.80
    
    def __init__(self):
        self.agent_name = "CollateralAgent"
        logger.info(f"{self.agent_name} initialized")
    
    async def process(self, application: LoanApplicationRequest) -> CollateralResult:
        """
        Verify collateral adequacy.
        
        Args:
            application: Loan application request
            
        Returns:
            CollateralResult with assessment
        """
        try:
            logger.info(f"{self.agent_name} verifying collateral for {application.name}")
            
            # Calculate LTV ratio
            ltv_ratio = self._calculate_ltv(
                application.loan_amount,
                application.collateral_value
            )
            
            # Calculate collateral coverage
            coverage = self._calculate_coverage(
                application.collateral_value,
                application.loan_amount
            )
            
            # Assess if collateral is adequate
            adequate = self._assess_adequacy(ltv_ratio, coverage)
            
            # Perform margin assessment
            margin_assessment = self._assess_margin(ltv_ratio, coverage)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                application,
                ltv_ratio,
                coverage,
                adequate,
                margin_assessment
            )
            
            result = CollateralResult(
                collateral_adequate=adequate,
                ltv_ratio=round(ltv_ratio, 3),
                collateral_coverage=round(coverage, 3),
                margin_assessment=margin_assessment,
                reasoning=reasoning,
                approved=adequate
            )
            
            logger.info(f"{self.agent_name} completed: adequate={adequate}, LTV={ltv_ratio:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _calculate_ltv(self, loan_amount: float, collateral_value: float) -> float:
        """
        Calculate Loan-to-Value (LTV) ratio.
        
        Args:
            loan_amount: Requested loan amount
            collateral_value: Value of collateral
            
        Returns:
            LTV ratio (0-1+)
        """
        if collateral_value <= 0:
            return float('inf')
        
        return loan_amount / collateral_value
    
    def _calculate_coverage(self, collateral_value: float, loan_amount: float) -> float:
        """
        Calculate collateral coverage percentage.
        
        Args:
            collateral_value: Value of collateral
            loan_amount: Requested loan amount
            
        Returns:
            Coverage as decimal (e.g., 1.2 = 120% coverage)
        """
        if loan_amount <= 0:
            return float('inf')
        
        return collateral_value / loan_amount
    
    def _assess_adequacy(self, ltv_ratio: float, coverage: float) -> bool:
        """
        Assess if collateral is adequate.
        
        Args:
            ltv_ratio: Loan-to-Value ratio
            coverage: Collateral coverage ratio
            
        Returns:
            True if collateral is adequate
        """
        # Collateral is adequate if:
        # 1. LTV is within acceptable range (≤ 80%)
        # 2. Coverage is at least minimum required (≥ 80% or 1.0/0.8 = 1.25x)
        
        ltv_acceptable = ltv_ratio <= self.MAX_LTV_RATIO
        coverage_sufficient = coverage >= (1.0 / self.MAX_LTV_RATIO)
        
        return ltv_acceptable and coverage_sufficient
    
    def _assess_margin(self, ltv_ratio: float, coverage: float) -> str:
        """
        Assess margin of safety.
        
        Args:
            ltv_ratio: Loan-to-Value ratio
            coverage: Collateral coverage ratio
            
        Returns:
            Margin assessment string
        """
        if ltv_ratio <= 0.60:
            return "Excellent - Strong collateral buffer (LTV ≤ 60%)"
        elif ltv_ratio <= 0.70:
            return "Good - Adequate collateral margin (LTV ≤ 70%)"
        elif ltv_ratio <= 0.80:
            return "Acceptable - Standard collateral margin (LTV ≤ 80%)"
        elif ltv_ratio <= 0.90:
            return "Marginal - Limited collateral buffer (LTV 80-90%)"
        elif ltv_ratio <= 1.0:
            return "Insufficient - Minimal collateral coverage (LTV 90-100%)"
        else:
            return "Inadequate - Collateral does not cover loan amount (LTV > 100%)"
    
    def _generate_reasoning(
        self,
        application: LoanApplicationRequest,
        ltv_ratio: float,
        coverage: float,
        adequate: bool,
        margin_assessment: str
    ) -> str:
        """
        Generate detailed reasoning for collateral assessment.
        
        Args:
            application: Loan application request
            ltv_ratio: Loan-to-Value ratio
            coverage: Collateral coverage ratio
            adequate: Whether collateral is adequate
            margin_assessment: Margin assessment string
            
        Returns:
            Reasoning string
        """
        lines = [
            f"Collateral Assessment for {application.name}:",
            f"• Loan Amount: ${application.loan_amount:,.2f}",
            f"• Collateral Value: ${application.collateral_value:,.2f}",
            f"• LTV Ratio: {ltv_ratio:.1%}",
            f"• Coverage: {coverage:.1%} ({coverage:.2f}x)",
            f"• Status: {'Adequate' if adequate else 'Inadequate'}",
            "",
            f"Margin Assessment: {margin_assessment}",
            ""
        ]
        
        # Calculate effective loan amount with margin
        effective_loan = application.collateral_value * self.MAX_LTV_RATIO
        
        lines.append("Analysis:")
        
        # LTV analysis
        if ltv_ratio <= self.MAX_LTV_RATIO:
            lines.append(f"✓ LTV ratio of {ltv_ratio:.1%} is within acceptable range (≤ {self.MAX_LTV_RATIO:.0%})")
        else:
            lines.append(f"✗ LTV ratio of {ltv_ratio:.1%} exceeds acceptable threshold ({self.MAX_LTV_RATIO:.0%})")
        
        # Coverage analysis
        if coverage >= 1.25:  # 125% coverage
            lines.append(f"✓ Excellent collateral coverage at {coverage:.1%}")
        elif coverage >= 1.0:
            lines.append(f"✓ Full collateral coverage at {coverage:.1%}")
        elif coverage >= 0.80:
            lines.append(f"⚠ Partial collateral coverage at {coverage:.1%}")
        else:
            lines.append(f"✗ Insufficient collateral coverage at {coverage:.1%}")
        
        # Effective lending capacity
        if application.collateral_value > 0:
            lines.append(f"• Maximum recommendable loan: ${effective_loan:,.2f} (at {self.MAX_LTV_RATIO:.0%} LTV)")
            
            if application.loan_amount <= effective_loan:
                difference = effective_loan - application.loan_amount
                lines.append(f"• Safety margin: ${difference:,.2f}")
            else:
                shortfall = application.loan_amount - effective_loan
                lines.append(f"• Shortfall: ${shortfall:,.2f} above recommended limit")
        
        # Final recommendation
        lines.append("")
        if adequate:
            lines.append("✓ Collateral verification successful. Adequate security for loan approval.")
        else:
            lines.append("✗ Collateral verification failed. Additional collateral or lower loan amount required.")
        
        return "\n".join(lines)
