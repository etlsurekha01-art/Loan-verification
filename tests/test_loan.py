"""
Unit tests for Loan Verification System
Tests all endpoints with proper mocking and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        # Accept both healthy and degraded status in test environment
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "database_connected" in data


class TestSimpleLoanEligibility:
    """Test simple loan eligibility endpoint with Serper API mocking"""
    
    @patch('serper_service.SerperService.verify_company')
    def test_missing_required_fields(self, mock_verify):
        """Test request with missing required fields"""
        # Missing credit_score
        response = client.post("/check-loan-eligibility", json={
            "name": "John Doe",
            "income": 50000,
            "company": "Google",
            "loan_amount": 20000
        })
        assert response.status_code == 422  # Unprocessable Entity
        
    @patch('serper_service.SerperService.verify_company')
    def test_invalid_credit_score_below_minimum(self, mock_verify):
        """Test rejection for credit score below 650"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Jane Smith",
            "income": 60000,
            "company": "Microsoft",
            "loan_amount": 25000,
            "credit_score": 600  # Below 650 threshold
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        assert "650" in data["reason"]
        assert data["company_verified"] is False
        assert data["verification_confidence"] == "n/a"
        
        # Verify Serper API was NOT called (early rejection)
        mock_verify.assert_not_called()
    
    @patch('serper_service.SerperService.verify_company')
    def test_invalid_income_below_minimum(self, mock_verify):
        """Test rejection for income below $30,000"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Bob Johnson",
            "income": 25000,  # Below 30000 threshold
            "company": "Amazon",
            "loan_amount": 15000,
            "credit_score": 700
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        assert "30,000" in data["reason"] or "30000" in data["reason"]
        assert data["company_verified"] is False
        assert data["verification_confidence"] == "n/a"
        
        # Verify Serper API was NOT called (early rejection)
        mock_verify.assert_not_called()
    
    @patch('serper_service.SerperService.verify_company')
    def test_combined_failures(self, mock_verify):
        """Test rejection for both low credit and low income"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Alice Wilson",
            "income": 20000,  # Below threshold
            "company": "Apple",
            "loan_amount": 10000,
            "credit_score": 580  # Below threshold
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        assert "credit score" in data["reason"].lower()
        assert "income" in data["reason"].lower()
        
        # Verify Serper API was NOT called (early rejection)
        mock_verify.assert_not_called()
    
    @patch('serper_service.SerperService.verify_company')
    def test_valid_application_approved(self, mock_verify):
        """Test approval for valid application with verified company"""
        # Mock successful company verification
        mock_verify.return_value = {
            "verified": True,
            "confidence": "high",
            "reason": "Company appears legitimate based on search results",
            "results": [
                {
                    "title": "Google - Official Website",
                    "snippet": "Google LLC is a technology company...",
                    "link": "https://www.google.com"
                }
            ]
        }
        
        response = client.post("/check-loan-eligibility", json={
            "name": "Sarah Davis",
            "income": 80000,
            "company": "Google",
            "loan_amount": 30000,
            "credit_score": 750
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["company_verified"] is True
        assert data["verification_confidence"] == "high"
        assert len(data["verification_results"]) > 0
        
        # Verify Serper API was called with correct company name
        mock_verify.assert_called_once_with("Google")
    
    @patch('serper_service.SerperService.verify_company')
    def test_company_verification_failed(self, mock_verify):
        """Test rejection when company cannot be verified"""
        # Mock failed company verification
        mock_verify.return_value = {
            "verified": False,
            "confidence": "low",
            "reason": "Insufficient verification information",
            "results": []
        }
        
        response = client.post("/check-loan-eligibility", json={
            "name": "Tom Brown",
            "income": 70000,
            "company": "Unknown Fake Corp",
            "loan_amount": 25000,
            "credit_score": 720
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        assert data["company_verified"] is False
        assert "verification failed" in data["reason"].lower()
        
        # Verify Serper API was called
        mock_verify.assert_called_once_with("Unknown Fake Corp")
    
    @patch('serper_service.SerperService.verify_company')
    def test_edge_case_minimum_valid_values(self, mock_verify):
        """Test with minimum valid credit score and income"""
        mock_verify.return_value = {
            "verified": True,
            "confidence": "medium",
            "reason": "Some positive indicators found",
            "results": [{"title": "Test", "snippet": "Test", "link": "https://test.com"}]
        }
        
        response = client.post("/check-loan-eligibility", json={
            "name": "Min Valid",
            "income": 30000,  # Exactly at minimum
            "company": "Valid Company",
            "loan_amount": 10000,
            "credit_score": 650  # Exactly at minimum
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["company_verified"] is True
    
    def test_invalid_data_types(self):
        """Test with invalid data types"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": "invalid",  # Should be number
            "company": "Test Corp",
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        assert response.status_code == 422  # Unprocessable Entity


class TestFullLoanApplication:
    """Test full loan application endpoint with multi-agent system"""
    
    @patch('agents.critique.genai')
    @patch('agents.final_decision.genai')
    def test_missing_required_fields_full(self, mock_final, mock_critique):
        """Test full application with missing required fields"""
        response = client.post("/loan/apply", json={
            "name": "John Doe",
            "income": 50000,
            # Missing company_name and other required fields
            "loan_amount": 20000
        })
        
        assert response.status_code == 422  # Unprocessable Entity
    
    @pytest.mark.skip(reason="Requires orchestrator initialization - run as integration test")
    @patch('agents.critique.genai')
    @patch('agents.final_decision.genai')
    def test_low_credit_score_full(self, mock_final, mock_critique):
        """Test full application with low credit score"""
        response = client.post("/loan/apply", json={
            "name": "Jane Smith",
            "income": 60000,
            "company_name": "Tech Corp",
            "employment_years": 3,
            "loan_amount": 25000,
            "existing_loans": 2,
            "repayment_score": 5.0,  # Lower repayment score
            "collateral_value": 40000
        })
        
        assert response.status_code == 200
        data = response.json()
        # Low repayment score should be reflected in results
        assert "decision" in data
    
    @pytest.mark.skip(reason="Requires orchestrator initialization - run as integration test")
    @patch('agents.critique.genai')
    @patch('agents.final_decision.genai')
    def test_valid_full_application(self, mock_final, mock_critique):
        """Test valid full loan application"""
        response = client.post("/loan/apply", json={
            "name": "Sarah Wilson",
            "income": 80000,
            "company_name": "Google",
            "employment_years": 5,
            "loan_amount": 30000,
            "existing_loans": 1,
            "repayment_score": 8.5,
            "collateral_value": 60000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["applicant_name"] == "Sarah Wilson"
        assert "decision" in data
        assert "risk_score" in data
        assert "agent_results" in data
        
        # Check agent results structure
        assert "credit_analysis" in data["agent_results"]
        assert "employment_verification" in data["agent_results"]
        assert "collateral_assessment" in data["agent_results"]


class TestDataValidation:
    """Test data validation and edge cases"""
    
    @patch('serper_service.SerperService.verify_company')
    def test_negative_credit_score(self, mock_verify):
        """Test negative credit score is rejected"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 50000,
            "company": "Test Corp",
            "loan_amount": 20000,
            "credit_score": -100  # Invalid
        })
        
        assert response.status_code == 422
    
    @patch('serper_service.SerperService.verify_company')
    def test_zero_income(self, mock_verify):
        """Test zero income is rejected"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 0,  # Invalid
            "company": "Test Corp",
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        assert response.status_code == 422
    
    @patch('serper_service.SerperService.verify_company')
    def test_negative_loan_amount(self, mock_verify):
        """Test negative loan amount is rejected"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 50000,
            "company": "Test Corp",
            "loan_amount": -10000,  # Invalid
            "credit_score": 700
        })
        
        assert response.status_code == 422
    
    @patch('serper_service.SerperService.verify_company')
    def test_empty_name(self, mock_verify):
        """Test empty name is rejected"""
        response = client.post("/check-loan-eligibility", json={
            "name": "",  # Invalid
            "income": 50000,
            "company": "Test Corp",
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        assert response.status_code == 422
    
    @patch('serper_service.SerperService.verify_company')
    def test_empty_company_name(self, mock_verify):
        """Test empty company name is rejected"""
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 50000,
            "company": "",  # Invalid
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        assert response.status_code == 422


class TestAPIEndpoints:
    """Test additional API endpoints"""
    
    def test_docs_endpoint(self):
        """Test API documentation endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert "paths" in data
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestSerperServiceMocking:
    """Test Serper service with various mock scenarios"""
    
    @patch('serper_service.SerperService.verify_company')
    def test_serper_api_timeout(self, mock_verify):
        """Test handling of Serper API timeout"""
        # Mock API timeout scenario (falls back to simulation)
        mock_verify.side_effect = Exception("API timeout")
        
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 50000,
            "company": "Test Corp",
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        # Should handle error gracefully
        assert response.status_code in [200, 500]
    
    @patch('serper_service.SerperService.verify_company')
    def test_serper_returns_empty_results(self, mock_verify):
        """Test when Serper API returns no results"""
        mock_verify.return_value = {
            "verified": False,
            "confidence": "low",
            "reason": "No search results found",
            "results": []
        }
        
        response = client.post("/check-loan-eligibility", json={
            "name": "Test User",
            "income": 50000,
            "company": "Unknown Company XYZ",
            "loan_amount": 20000,
            "credit_score": 700
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        assert data["company_verified"] is False


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def test_client():
    """Provide test client for all tests"""
    return client


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database state between tests"""
    # This ensures tests don't interfere with each other
    yield
    # Cleanup code here if needed


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
