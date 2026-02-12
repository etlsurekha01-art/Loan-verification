"""
Agentic AI Loan Eligibility Verification System
FastAPI application with multi-agent architecture for automated loan processing.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from models import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    HealthResponse
)
from simple_loan_models import (
    SimpleLoanRequest,
    SimpleLoanResponse,
    VerificationResult
)
from database import Database, get_database
from orchestrator import OrchestratorAgent
from serper_service import get_serper_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
database: Database = None
orchestrator: OrchestratorAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    global database, orchestrator
    
    logger.info("Starting Agentic AI Loan Verification System...")
    
    # Initialize database
    database = get_database()
    await database.initialize()
    logger.info("Database initialized")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(database)
    logger.info("Orchestrator agent initialized")
    
    # Verify Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("GEMINI_API_KEY not configured - AI features will use fallback logic")
    else:
        logger.info("Gemini AI integration enabled")
    
    logger.info("System ready to process loan applications")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agentic AI Loan Verification System...")


# Create FastAPI application
app = FastAPI(
    title="Agentic AI Loan Verification System",
    description="""
    A sophisticated multi-agent system for automated loan eligibility verification.
    
    ## Features
    
    * **Multi-Agent Architecture**: Specialized agents for different verification tasks
    * **Credit Analysis**: Deterministic credit risk evaluation
    * **Employment Verification**: Simulated web-based employment checks
    * **Collateral Assessment**: LTV ratio and coverage analysis
    * **AI-Powered Critique**: Quality review and decision enhancement
    * **Comprehensive Logging**: Full audit trail of all decisions
    
    ## Agents
    
    1. **Orchestrator**: Coordinates all verification activities
    2. **Greeting**: Initial acknowledgement
    3. **Planner**: Task breakdown and planning
    4. **Credit**: Credit history and risk analysis
    5. **Employment**: Employment and company verification
    6. **Collateral**: Collateral value assessment
    7. **Critique**: Quality review and consistency check
    8. **Final Decision**: Ultimate approval/rejection decision
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    """
    Serve the web UI for loan applications.
    """
    return FileResponse("index.html")


@app.get("/api", tags=["General"])
async def api_root():
    """
    API root endpoint with system information.
    """
    return {
        "system": "Agentic AI Loan Verification System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ui": "/",
            "apply": "/loan/apply",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint to verify system status.
    
    Returns:
        HealthResponse with system health information
    """
    try:
        # Check database connection
        db_connected = await database.check_connection() if database else False
        
        return HealthResponse(
            status="healthy" if db_connected else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            database_connected=db_connected
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            database_connected=False
        )


@app.post(
    "/loan/apply",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Loan Processing"]
)
async def apply_for_loan(application: LoanApplicationRequest):
    """
    Submit a loan application for verification.
    
    The application will be processed through multiple verification agents:
    - Credit history analysis
    - Employment verification
    - Collateral assessment
    - Risk evaluation
    - Final decision
    
    Args:
        application: Loan application details
        
    Returns:
        LoanApplicationResponse with decision and comprehensive analysis
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"Received loan application from {application.name} for ${application.loan_amount:,.2f}")
        
        # Validate orchestrator is initialized
        if not orchestrator:
            logger.error("Orchestrator not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready. Please try again later."
            )
        
        # Process application through orchestrator
        response = await orchestrator.process_application(application)
        
        logger.info(
            f"Application processed for {application.name}: "
            f"{response.decision.value} (risk: {response.risk_score:.3f})"
        )
        
        return response
        
    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid application data: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Error processing loan application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your application. Please try again later."
        )


@app.post(
    "/check-loan-eligibility",
    response_model=SimpleLoanResponse,
    status_code=status.HTTP_200_OK,
    tags=["Simple Loan Check"]
)
async def check_loan_eligibility(request: SimpleLoanRequest):
    """
    Simple loan eligibility check with Serper.dev company verification.
    
    Flow:
    1. Validate input fields
    2. Check credit score (minimum 650)
    3. Check income (minimum $30,000)
    4. Verify company using Serper.dev API
    5. Make final decision
    
    Args:
        request: Simple loan request with name, income, company, loan_amount, credit_score
        
    Returns:
        SimpleLoanResponse with APPROVED/REJECTED status and reasoning
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Simple eligibility check for {request.name} - {request.company}")
        
        # Step 1: Input validation (handled by Pydantic)
        
        # Step 2: Basic eligibility logic
        MIN_CREDIT_SCORE = 650
        MIN_INCOME = 30000
        
        rejection_reasons = []
        
        # Check credit score
        if request.credit_score < MIN_CREDIT_SCORE:
            rejection_reasons.append(f"Credit score {request.credit_score} is below minimum requirement of {MIN_CREDIT_SCORE}")
        
        # Check income
        if request.income < MIN_INCOME:
            rejection_reasons.append(f"Income ${request.income:,.2f} is below minimum requirement of ${MIN_INCOME:,.2f}")
        
        # If basic checks fail, reject immediately
        if rejection_reasons:
            logger.info(f"Application rejected for {request.name}: {'; '.join(rejection_reasons)}")
            return SimpleLoanResponse(
                status="REJECTED",
                reason="; ".join(rejection_reasons),
                verification_results=[],
                company_verified=False,
                verification_confidence="n/a"
            )
        
        # Step 3: External company verification using Serper API
        serper_service = get_serper_service()
        verification_data = serper_service.verify_company(request.company)
        
        company_verified = verification_data.get("verified", False)
        confidence = verification_data.get("confidence", "low")
        verification_reason = verification_data.get("reason", "")
        search_results = verification_data.get("results", [])
        
        # Convert to VerificationResult objects
        verification_results = [
            VerificationResult(
                title=result.get("title", ""),
                snippet=result.get("snippet", ""),
                link=result.get("link", "")
            )
            for result in search_results
        ]
        
        # Step 4: Final decision
        if company_verified:
            # All checks passed - APPROVED
            reason = (
                f"Credit score is {request.credit_score}, income meets requirements (${request.income:,.2f}), "
                f"and company {request.company} has been verified as legitimate ({confidence} confidence). "
                f"{verification_reason}"
            )
            
            logger.info(f"Application APPROVED for {request.name}")
            return SimpleLoanResponse(
                status="APPROVED",
                reason=reason,
                verification_results=verification_results,
                company_verified=True,
                verification_confidence=confidence
            )
        else:
            # Company verification failed
            reason = (
                f"While credit score ({request.credit_score}) and income (${request.income:,.2f}) meet requirements, "
                f"company verification failed: {verification_reason}"
            )
            
            logger.info(f"Application REJECTED for {request.name}: Company verification failed")
            return SimpleLoanResponse(
                status="REJECTED",
                reason=reason,
                verification_results=verification_results,
                company_verified=False,
                verification_confidence=confidence
            )
            
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request data: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error checking loan eligibility: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while checking eligibility. Please try again later."
        )


@app.get("/loan/task/{task_id}", tags=["Loan Processing"])
async def get_task_status(task_id: str):
    """
    Get the status of a specific loan verification task.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Task status and results (if completed)
        
    Raises:
        HTTPException: If task not found
    """
    try:
        if not orchestrator:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
        
        task_status = await orchestrator.get_task_status(task_id)
        
        if task_status.get("status") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return task_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task status"
        )


@app.get("/loan/recent", tags=["Loan Processing"])
async def get_recent_applications(limit: int = 10):
    """
    Get recent loan applications.
    
    Args:
        limit: Maximum number of applications to return (default: 10, max: 100)
        
    Returns:
        List of recent application summaries
    """
    try:
        if not orchestrator:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
        
        # Limit the maximum number of results
        limit = min(max(1, limit), 100)
        
        recent_tasks = await orchestrator.get_recent_tasks(limit)
        
        return {
            "count": len(recent_tasks),
            "limit": limit,
            "tasks": recent_tasks
        }
        
    except Exception as e:
        logger.error(f"Error retrieving recent applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving recent applications"
        )


@app.get("/stats", tags=["General"])
async def get_statistics():
    """
    Get system statistics.
    
    Returns:
        Database and processing statistics
    """
    try:
        if not database:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
        
        stats = await database.get_statistics()
        
        return {
            "system": "Agentic AI Loan Verification System",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
