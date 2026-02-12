"""
Greeting Agent - Initial acknowledgement and welcome message.
First agent to respond to loan application.
"""

import logging
from datetime import datetime
from models import GreetingResult, LoanApplicationRequest

logger = logging.getLogger(__name__)


class GreetingAgent:
    """
    Greeting Agent sends initial acknowledgement to loan applicants.
    Provides a friendly welcome message and confirms receipt of application.
    """
    
    def __init__(self):
        self.agent_name = "GreetingAgent"
        logger.info(f"{self.agent_name} initialized")
    
    async def process(self, application: LoanApplicationRequest) -> GreetingResult:
        """
        Process loan application and generate greeting message.
        
        Args:
            application: Loan application request
            
        Returns:
            GreetingResult with welcome message
        """
        try:
            logger.info(f"{self.agent_name} processing application for {application.name}")
            
            # Generate personalized greeting
            message = self._generate_greeting(application)
            
            result = GreetingResult(
                message=message,
                timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"{self.agent_name} completed for {application.name}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            # Return generic greeting on error
            return GreetingResult(
                message=f"Dear Applicant, we have received your loan application.",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _generate_greeting(self, application: LoanApplicationRequest) -> str:
        """
        Generate personalized greeting message.
        
        Args:
            application: Loan application request
            
        Returns:
            Greeting message string
        """
        # Format loan amount with commas
        loan_amount_formatted = f"${application.loan_amount:,.2f}"
        
        message = (
            f"Dear {application.name},\n\n"
            f"Thank you for applying for a loan of {loan_amount_formatted} with our institution. "
            f"We have received your application and it is now being processed by our "
            f"advanced verification system.\n\n"
            f"Our multi-agent verification system will thoroughly evaluate:\n"
            f"- Your credit history and financial standing\n"
            f"- Employment verification and stability\n"
            f"- Collateral assessment\n"
            f"- Overall risk analysis\n\n"
            f"You will receive a comprehensive decision shortly. "
            f"Thank you for choosing our services."
        )
        
        return message
