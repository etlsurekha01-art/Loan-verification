#!/usr/bin/env python3
"""
Test script for the Agentic AI Loan Verification System.
Demonstrates various loan application scenarios.
"""

import requests
import json
import time
from typing import Dict, Any


# API endpoint (adjust if needed)
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_result(response: Dict[Any, Any]):
    """Pretty print the API response"""
    print(f"Decision: {response['decision']}")
    print(f"Risk Score: {response['risk_score']:.3f}")
    print(f"\nReasoning:")
    print(response['reasoning'])
    
    if response.get('agent_summary'):
        summary = response['agent_summary']
        
        if summary.get('credit'):
            credit = summary['credit']
            print(f"\n📊 Credit Analysis:")
            print(f"   Risk: {credit['risk_category']} ({credit['risk_score']:.3f})")
            print(f"   Credit Score: {credit['credit_score']:.1f}/10")
        
        if summary.get('employment'):
            employment = summary['employment']
            print(f"\n💼 Employment Verification:")
            print(f"   Verified: {employment['employment_verified']}")
            print(f"   Stability: {employment['employment_stability']}")
        
        if summary.get('collateral'):
            collateral = summary['collateral']
            print(f"\n🏠 Collateral Assessment:")
            print(f"   Adequate: {collateral['collateral_adequate']}")
            print(f"   LTV Ratio: {collateral['ltv_ratio']:.1%}")
    
    print()


def test_application(name: str, data: Dict[str, Any]):
    """Submit a test loan application"""
    print_section(f"Test Case: {name}")
    
    print("Application Details:")
    print(json.dumps(data, indent=2))
    print("\nSubmitting application...")
    
    try:
        response = requests.post(f"{BASE_URL}/loan/apply", json=data)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ Application Processed Successfully\n")
        print_result(result)
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def test_health():
    """Test the health endpoint"""
    print_section("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Database Connected: {result['database_connected']}")
        print(f"Version: {result['version']}")
        print("✅ System is healthy\n")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Run all test cases"""
    print_section("Agentic AI Loan Verification System - Test Suite")
    
    # Check if system is healthy
    if not test_health():
        print("\n⚠️  System is not healthy. Please start the server first:")
        print("   uvicorn main:app --reload")
        return
    
    time.sleep(1)
    
    # Test Case 1: Strong Applicant (Should be APPROVED)
    test_application(
        "Strong Applicant - Expected: APPROVED",
        {
            "name": "Alice Johnson",
            "income": 100000.0,
            "loan_amount": 30000.0,
            "existing_loans": 0,
            "repayment_score": 9.5,
            "employment_years": 10.0,
            "company_name": "Microsoft",
            "collateral_value": 50000.0
        }
    )
    
    time.sleep(2)
    
    # Test Case 2: Moderate Applicant (Should be CONDITIONAL)
    test_application(
        "Moderate Applicant - Expected: CONDITIONAL",
        {
            "name": "Bob Smith",
            "income": 60000.0,
            "loan_amount": 45000.0,
            "existing_loans": 2,
            "repayment_score": 7.0,
            "employment_years": 3.5,
            "company_name": "Tech Startup Inc",
            "collateral_value": 50000.0
        }
    )
    
    time.sleep(2)
    
    # Test Case 3: Weak Applicant (Should be REJECTED)
    test_application(
        "Weak Applicant - Expected: REJECTED",
        {
            "name": "Charlie Wilson",
            "income": 30000.0,
            "loan_amount": 50000.0,
            "existing_loans": 4,
            "repayment_score": 3.5,
            "employment_years": 0.5,
            "company_name": "Unknown Company",
            "collateral_value": 15000.0
        }
    )
    
    time.sleep(2)
    
    # Test Case 4: Good Credit, Poor Employment (Should be CONDITIONAL)
    test_application(
        "Good Credit, Poor Employment - Expected: CONDITIONAL",
        {
            "name": "Diana Martinez",
            "income": 80000.0,
            "loan_amount": 40000.0,
            "existing_loans": 1,
            "repayment_score": 8.5,
            "employment_years": 0.8,
            "company_name": "Recent Employer LLC",
            "collateral_value": 60000.0
        }
    )
    
    time.sleep(2)
    
    # Test Case 5: Excellent Profile (Should be APPROVED)
    test_application(
        "Excellent Profile - Expected: APPROVED",
        {
            "name": "Emily Chen",
            "income": 120000.0,
            "loan_amount": 35000.0,
            "existing_loans": 0,
            "repayment_score": 9.8,
            "employment_years": 8.0,
            "company_name": "Google",
            "collateral_value": 75000.0
        }
    )
    
    time.sleep(2)
    
    # Check recent applications
    print_section("Recent Applications")
    try:
        response = requests.get(f"{BASE_URL}/loan/recent?limit=5")
        response.raise_for_status()
        
        result = response.json()
        print(f"Total Recent Applications: {result['count']}\n")
        
        for task in result['tasks']:
            print(f"• {task['applicant_name']}: {task.get('decision', 'Processing...')}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving recent applications: {e}")
    
    print_section("Test Suite Complete")
    print("✅ All test cases executed successfully!")
    print("\nTo view the interactive API documentation, visit:")
    print(f"   {BASE_URL}/docs")


if __name__ == "__main__":
    main()
