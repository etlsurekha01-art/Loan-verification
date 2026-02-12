"""
Orchestrator Agent - Coordinates all sub-agents for loan verification.
Manages the workflow and maintains task state.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from models import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    AgentSummary,
    LoanTask,
    TaskStatus
)
from database import Database
from agents import (
    GreetingAgent,
    PlannerAgent,
    CreditAgent,
    EmploymentAgent,
    CollateralAgent,
    CritiqueAgent,
    FinalDecisionAgent
)

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator Agent coordinates all verification agents.
    Manages the complete loan verification workflow from start to finish.
    """
    
    def __init__(self, database: Database):
        """
        Initialize orchestrator with all sub-agents.
        
        Args:
            database: Database instance for task persistence
        """
        self.agent_name = "OrchestratorAgent"
        self.database = database
        
        # Initialize all sub-agents
        self.greeting_agent = GreetingAgent()
        self.planner_agent = PlannerAgent()
        self.credit_agent = CreditAgent()
        self.employment_agent = EmploymentAgent()
        self.collateral_agent = CollateralAgent()
        self.critique_agent = CritiqueAgent()
        self.final_decision_agent = FinalDecisionAgent()
        
        logger.info(f"{self.agent_name} initialized with all sub-agents")
    
    async def process_application(
        self, 
        application: LoanApplicationRequest
    ) -> LoanApplicationResponse:
        """
        Process complete loan application through all agents.
        
        Args:
            application: Loan application request
            
        Returns:
            LoanApplicationResponse with decision and details
        """
        task_id = self._generate_task_id()
        
        try:
            logger.info(f"{self.agent_name} starting verification for {application.name} (task: {task_id})")
            
            # Create task in database
            await self._create_task(task_id, application)
            
            # Update task status to in-progress
            await self.database.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            
            # Stage 1: Greeting & Planning
            logger.info(f"[{task_id}] Stage 1: Greeting and Planning")
            greeting_result = await self.greeting_agent.process(application)
            planner_result = await self.planner_agent.process(application)
            
            # Stage 2: Parallel Verification (Credit, Employment, Collateral)
            logger.info(f"[{task_id}] Stage 2: Parallel Verification")
            credit_result = await self.credit_agent.process(application)
            employment_result = await self.employment_agent.process(application)
            collateral_result = await self.collateral_agent.process(application)
            
            # Stage 3: Quality Review
            logger.info(f"[{task_id}] Stage 3: Quality Review")
            critique_result = await self.critique_agent.process(
                application,
                credit_result,
                employment_result,
                collateral_result
            )
            
            # Stage 4: Final Decision
            logger.info(f"[{task_id}] Stage 4: Final Decision")
            final_decision = await self.final_decision_agent.process(
                application,
                credit_result,
                employment_result,
                collateral_result,
                critique_result
            )
            
            # Compile agent summary
            agent_summary = AgentSummary(
                greeting=greeting_result,
                planner=planner_result,
                credit=credit_result,
                employment=employment_result,
                collateral=collateral_result,
                critique=critique_result,
                final_decision=final_decision
            )
            
            # Create response
            response = LoanApplicationResponse(
                decision=final_decision.decision,
                risk_score=final_decision.risk_score,
                reasoning=final_decision.reasoning,
                agent_summary=agent_summary,
                task_id=task_id,
                processed_at=datetime.utcnow().isoformat()
            )
            
            # Store result in database
            await self._complete_task(task_id, response)
            
            logger.info(f"[{task_id}] Verification complete: {final_decision.decision.value}")
            return response
            
        except Exception as e:
            logger.error(f"[{task_id}] {self.agent_name} error: {e}")
            
            # Mark task as failed
            await self.database.update_task_status(
                task_id, 
                TaskStatus.FAILED,
                error_message=str(e)
            )
            
            raise
    
    def _generate_task_id(self) -> str:
        """
        Generate unique task identifier.
        
        Returns:
            Task ID string
        """
        return f"task_{uuid.uuid4().hex[:12]}"
    
    async def _create_task(
        self, 
        task_id: str, 
        application: LoanApplicationRequest
    ) -> bool:
        """
        Create task record in database.
        
        Args:
            task_id: Task identifier
            application: Loan application request
            
        Returns:
            True if successful
        """
        try:
            task = LoanTask(
                task_id=task_id,
                applicant_name=application.name,
                status=TaskStatus.PENDING,
                request_data=application.dict(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return await self.database.create_task(task)
            
        except Exception as e:
            logger.error(f"Error creating task {task_id}: {e}")
            return False
    
    async def _complete_task(
        self, 
        task_id: str, 
        response: LoanApplicationResponse
    ) -> bool:
        """
        Mark task as completed and store results.
        
        Args:
            task_id: Task identifier
            response: Loan application response
            
        Returns:
            True if successful
        """
        try:
            # Convert response to dict for storage
            result_data = response.dict()
            
            return await self.database.update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                result_data=result_data
            )
            
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a specific task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status information
        """
        try:
            task = await self.database.get_task(task_id)
            
            if task:
                return {
                    "task_id": task.task_id,
                    "applicant_name": task.applicant_name,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "result": task.result_data if task.result_data else None,
                    "error": task.error_message
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "not_found",
                    "error": "Task not found in database"
                }
                
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    async def get_recent_tasks(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get recent task summaries.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of task summaries
        """
        try:
            tasks = await self.database.get_recent_tasks(limit)
            
            return [
                {
                    "task_id": task.task_id,
                    "applicant_name": task.applicant_name,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "decision": task.result_data.get("decision") if task.result_data else None
                }
                for task in tasks
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent tasks: {e}")
            return []
