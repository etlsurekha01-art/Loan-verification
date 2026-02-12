"""
Planner Agent - Breaks down loan verification into subtasks.
Analyzes the application and creates an execution plan.
"""

import logging
from models import PlannerResult, LoanApplicationRequest

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Planner Agent analyzes the loan application and creates a verification plan.
    Determines which checks are needed and their execution order.
    """
    
    def __init__(self):
        self.agent_name = "PlannerAgent"
        logger.info(f"{self.agent_name} initialized")
    
    async def process(self, application: LoanApplicationRequest) -> PlannerResult:
        """
        Create verification plan for loan application.
        
        Args:
            application: Loan application request
            
        Returns:
            PlannerResult with task breakdown
        """
        try:
            logger.info(f"{self.agent_name} creating plan for {application.name}")
            
            # Define verification tasks
            tasks = self._identify_tasks(application)
            
            # Define execution order
            execution_order = self._determine_execution_order(tasks)
            
            # Estimate duration
            duration = self._estimate_duration(len(tasks))
            
            result = PlannerResult(
                tasks=tasks,
                execution_order=execution_order,
                estimated_duration=duration
            )
            
            logger.info(f"{self.agent_name} plan created with {len(tasks)} tasks")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _identify_tasks(self, application: LoanApplicationRequest) -> list[str]:
        """
        Identify necessary verification tasks based on application.
        
        Args:
            application: Loan application request
            
        Returns:
            List of task descriptions
        """
        tasks = [
            "Credit History Verification - Analyze debt-to-income ratio, existing loans, and repayment history",
            "Employment Verification - Verify employment status, company legitimacy, and job stability",
            "Collateral Verification - Assess collateral value and loan-to-value ratio",
            "Risk Assessment - Calculate overall risk score and category",
            "Quality Review - Critique and validate all verification results",
            "Final Decision - Make approval/rejection decision with reasoning"
        ]
        
        # Add additional checks based on application characteristics
        if application.existing_loans > 2:
            tasks.insert(1, "Enhanced Debt Analysis - Multiple existing loans detected")
        
        if application.employment_years < 1:
            tasks.insert(2, "Enhanced Employment Verification - Recent employment change")
        
        if application.loan_amount > application.income * 2:
            tasks.insert(3, "High Loan-to-Income Review - Loan amount exceeds 2x annual income")
        
        return tasks
    
    def _determine_execution_order(self, tasks: list[str]) -> list[str]:
        """
        Determine optimal execution order for tasks.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Ordered list of task stages
        """
        return [
            "Stage 1: Parallel Verification - Credit, Employment, and Collateral checks",
            "Stage 2: Quality Review - Critique agent validates all results",
            "Stage 3: Final Decision - Generate approval/rejection decision"
        ]
    
    def _estimate_duration(self, task_count: int) -> str:
        """
        Estimate processing duration.
        
        Args:
            task_count: Number of tasks
            
        Returns:
            Duration estimate string
        """
        # Each task takes approximately 2-3 seconds
        estimated_seconds = task_count * 2.5
        
        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)} seconds"
        else:
            minutes = int(estimated_seconds / 60)
            return f"~{minutes} minute{'s' if minutes > 1 else ''}"
