"""
Test script for the simple loan eligibility endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_approved_case():
    """Test case that should be APPROVED"""
    print("\n" + "="*60)
    print("TEST 1: APPROVED Case (Good credit, good income, real company)")
    print("="*60)
    
    data = {
        "name": "John Smith",
        "income": 75000,
        "company": "Google",
        "loan_amount": 25000,
        "credit_score": 720
    }
    
    response = requests.post(f"{BASE_URL}/check-loan-eligibility", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def test_low_credit_rejection():
    """Test case that should be REJECTED due to low credit score"""
    print("\n" + "="*60)
    print("TEST 2: REJECTED Case (Low credit score)")
    print("="*60)
    
    data = {
        "name": "Jane Doe",
        "income": 80000,
        "company": "Microsoft",
        "loan_amount": 30000,
        "credit_score": 600  # Below 650 threshold
    }
    
    response = requests.post(f"{BASE_URL}/check-loan-eligibility", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def test_low_income_rejection():
    """Test case that should be REJECTED due to low income"""
    print("\n" + "="*60)
    print("TEST 3: REJECTED Case (Low income)")
    print("="*60)
    
    data = {
        "name": "Bob Johnson",
        "income": 25000,  # Below 30000 threshold
        "company": "Amazon",
        "loan_amount": 15000,
        "credit_score": 700
    }
    
    response = requests.post(f"{BASE_URL}/check-loan-eligibility", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def test_suspicious_company():
    """Test case with suspicious/unknown company"""
    print("\n" + "="*60)
    print("TEST 4: Suspicious Company")
    print("="*60)
    
    data = {
        "name": "Alice Brown",
        "income": 50000,
        "company": "XYZ Fake Corp 12345",
        "loan_amount": 20000,
        "credit_score": 680
    }
    
    response = requests.post(f"{BASE_URL}/check-loan-eligibility", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def test_combined_failure():
    """Test case with multiple issues"""
    print("\n" + "="*60)
    print("TEST 5: Combined Failure (Low credit + Low income)")
    print("="*60)
    
    data = {
        "name": "Charlie Wilson",
        "income": 20000,  # Below threshold
        "company": "Apple",
        "loan_amount": 10000,
        "credit_score": 580  # Below threshold
    }
    
    response = requests.post(f"{BASE_URL}/check-loan-eligibility", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("\n🧪 Testing Simple Loan Eligibility Endpoint")
    print("=" * 60)
    
    try:
        # Check if server is running
        health_check = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✅ Server is running: {health_check.json()}")
        
        # Run tests
        test_approved_case()
        test_low_credit_rejection()
        test_low_income_rejection()
        test_suspicious_company()
        test_combined_failure()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server at http://localhost:8000")
        print("Please make sure the FastAPI server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
