# CI/CD Pipeline Documentation

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Agentic AI Loan Verification System.

---

## 🚀 Pipeline Architecture

### Workflows

1. **`ci-cd.yml`** - Main CI/CD pipeline (runs on push to main/develop)
2. **`pr-tests.yml`** - Pull request validation (runs on PRs)

### Pipeline Stages

```
┌─────────────┐
│   Push/PR   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Parallel Execution              │
├─────────────┬─────────────┬─────────────┤
│   Tests     │  Security   │ Code Quality│
│   (Job 1)   │  (Job 2)    │  (Job 4)    │
└──────┬──────┴──────┬──────┴──────┬──────┘
       │             │              │
       └─────────────┼──────────────┘
                     ▼
              ┌─────────────┐
              │Build Docker │
              │   (Job 3)   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   Deploy    │
              │  (Optional) │
              └─────────────┘
```

---

## 📋 Jobs Description

### Job 1: Test
**Purpose**: Run comprehensive test suite

**Steps**:
1. ✅ Checkout code
2. ✅ Setup Python 3.10 & 3.11 (matrix)
3. ✅ Install dependencies from `requirements.txt`
4. ✅ Create test environment file
5. ✅ Run linting with flake8
6. ✅ Execute pytest with coverage
7. ✅ Upload coverage to Codecov
8. ✅ Archive test results

**Triggers**: Push, Pull Request  
**Fail Condition**: Any test fails  
**Artifacts**: Coverage reports, test results

### Job 2: Security
**Purpose**: Scan for security vulnerabilities

**Steps**:
1. ✅ Run safety check (dependency vulnerabilities)
2. ✅ Run bandit (Python code security)
3. ✅ Generate security reports

**Triggers**: After tests pass  
**Fail Condition**: Critical vulnerabilities found  
**Artifacts**: Security reports

### Job 3: Build
**Purpose**: Build and test Docker image

**Steps**:
1. ✅ Setup Docker Buildx
2. ✅ Login to GitHub Container Registry
3. ✅ Extract Docker metadata
4. ✅ Build Docker image
5. ✅ Test Docker container health
6. ✅ Push image to registry (on main branch)

**Triggers**: After tests pass  
**Fail Condition**: Build fails or container unhealthy  
**Artifacts**: Docker image

### Job 4: Code Quality
**Purpose**: Ensure code quality standards

**Steps**:
1. ✅ Check formatting with Black
2. ✅ Check import sorting with isort
3. ✅ Run pylint analysis

**Triggers**: On all pushes/PRs  
**Fail Condition**: None (informational)  
**Artifacts**: Quality reports

### Job 5: Integration Tests
**Purpose**: Run tests against real APIs

**Steps**:
1. ✅ Run integration tests with real API keys
2. ✅ Conditional on secrets availability

**Triggers**: Only on main branch push  
**Fail Condition**: Integration tests fail  
**Required Secrets**: `GEMINI_API_KEY`, `SERPER_API_KEY`

### Job 6: Notify
**Purpose**: Send deployment notifications

**Steps**:
1. ✅ Send success notification
2. ✅ Log deployment details

**Triggers**: After all jobs succeed on main  
**Fail Condition**: None

---

## 🧪 Testing Framework

### Test Structure

```
tests/
├── __init__.py
└── test_loan.py        # Main test file
```

### Test Classes

1. **TestHealthEndpoint**: Health check tests
2. **TestSimpleLoanEligibility**: Simple endpoint tests with mocking
3. **TestFullLoanApplication**: Full multi-agent system tests
4. **TestDataValidation**: Input validation tests
5. **TestAPIEndpoints**: Additional endpoint tests
6. **TestSerperServiceMocking**: Serper API mock scenarios

### Test Coverage

- ✅ Unit tests for all endpoints
- ✅ Missing input field validation
- ✅ Invalid credit score (<650)
- ✅ Invalid income (<30,000)
- ✅ Valid application approval
- ✅ Company verification scenarios
- ✅ Edge cases and error handling
- ✅ Serper API mocking (no real API calls)

### Running Tests Locally

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test class
pytest tests/test_loan.py::TestSimpleLoanEligibility -v

# Run specific test
pytest tests/test_loan.py::TestSimpleLoanEligibility::test_invalid_credit_score_below_minimum -v
```

---

## 🔐 Environment Variables & Secrets

### Required Secrets (GitHub Repository Settings)

**For Integration Tests (Optional)**:
- `GEMINI_API_KEY` - Google Gemini API key
- `SERPER_API_KEY` - Serper.dev API key

### Setting Up Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets:
   - Name: `GEMINI_API_KEY`
   - Value: Your actual Gemini API key

### Environment Variables in CI

```yaml
env:
  GEMINI_API_KEY: test_key_for_ci
  SERPER_API_KEY: test_key_for_ci
  DATABASE_PATH: ./test_loan_verification.db
```

**Note**: Tests use mock values; real API keys only needed for integration tests.

---

## 🐳 Docker Build

### Build Process

The pipeline builds a Docker image with:
- Multi-stage build optimization
- Layer caching for faster builds
- Security scanning
- Health checks
- Automated testing

### Docker Image Tags

Images are tagged with:
- `latest` - Latest main branch build
- `main-<sha>` - Specific commit
- `pr-<number>` - Pull request builds

### Registry

Images pushed to: `ghcr.io/etlsurekha01-art/loan-verification`

---

## 📊 Code Coverage

### Coverage Requirements

- Minimum coverage: **70%**
- Coverage reports generated in: `htmlcov/`
- XML report for Codecov integration

### Viewing Coverage

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html
```

---

## ⚠️ Failure Handling

### Test Failures

**What happens**:
1. Pipeline stops immediately (fail-fast)
2. Subsequent jobs cancelled
3. PR marked as failed
4. Build artifacts preserved for debugging

**Recovery**:
1. Review test logs in GitHub Actions
2. Fix failing tests locally
3. Push fix
4. Pipeline re-runs automatically

### Build Failures

**Common causes**:
- Docker build errors
- Missing dependencies
- Container health check fails

**Resolution**:
1. Check Docker logs in Actions
2. Test Docker build locally: `docker build -t test .`
3. Fix Dockerfile or dependencies
4. Re-push

### Security Scan Failures

**Handling**:
- Security scans are informational (continue-on-error)
- Review security reports in artifacts
- Update vulnerable dependencies

---

## 🔄 Workflow Triggers

### Main CI/CD Pipeline

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # Manual trigger
```

### PR Tests

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

---

## 📈 Performance Optimization

### Caching

- **Python packages**: Cached using `actions/setup-python@v5` with `cache: 'pip'`
- **Docker layers**: Cached using GitHub Actions cache (`type=gha`)

### Parallel Execution

Jobs run in parallel where possible:
- Tests run on Python 3.10 & 3.11 simultaneously
- Security, code quality, and tests run concurrently

### Build Time

Average pipeline execution: **5-8 minutes**
- Tests: ~2 minutes
- Docker build: ~3 minutes
- Security scan: ~1 minute

---

## 🛠️ Local Development Workflow

### Pre-commit Testing

```bash
# Run tests before committing
pytest tests/ -v

# Check code formatting
black --check .
isort --check-only .

# Run linting
flake8 .
```

### Pre-push Checklist

- [ ] All tests pass locally
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] No linting errors
- [ ] Documentation updated
- [ ] `.env` not committed

---

## 🚢 Deployment

### Manual Deployment

```bash
# Trigger workflow manually
gh workflow run ci-cd.yml

# Or via GitHub UI:
# Actions → CI/CD Pipeline → Run workflow
```

### Automated Deployment

Pipeline automatically:
1. Builds Docker image on main branch push
2. Pushes to GitHub Container Registry
3. Tags with version/commit SHA

### Using the Built Image

```bash
# Pull latest image
docker pull ghcr.io/etlsurekha01-art/loan-verification:latest

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e SERPER_API_KEY=your_key \
  ghcr.io/etlsurekha01-art/loan-verification:latest
```

---

## 🐛 Debugging CI/CD Issues

### View Logs

```bash
# Install GitHub CLI
gh auth login

# View workflow runs
gh run list

# View specific run logs
gh run view <run-id> --log
```

### Common Issues

#### Tests Pass Locally but Fail in CI

**Causes**:
- Environment differences
- Missing dependencies
- Database state

**Solution**:
```bash
# Replicate CI environment
docker run -it --rm python:3.10 bash
pip install -r requirements.txt
pytest tests/ -v
```

#### Docker Build Fails

**Causes**:
- Large image size
- Network timeouts
- Missing files

**Solution**:
```bash
# Test build locally
docker build -t test .
docker run test
```

#### Coverage Below Threshold

**Causes**:
- Untested code paths
- Missing test cases

**Solution**:
```bash
# Generate coverage report
pytest --cov=. --cov-report=term-missing

# Add tests for uncovered lines
```

---

## 📚 Best Practices

### ✅ Do's

- ✅ Write tests for all new features
- ✅ Keep coverage above 70%
- ✅ Use descriptive test names
- ✅ Mock external API calls
- ✅ Test error conditions
- ✅ Update documentation
- ✅ Use environment variables for secrets

### ❌ Don'ts

- ❌ Commit API keys or secrets
- ❌ Skip tests to pass CI
- ❌ Make real API calls in tests
- ❌ Hardcode configuration
- ❌ Ignore security warnings
- ❌ Push directly to main without PR

---

## 🔍 Monitoring & Metrics

### GitHub Actions Dashboard

Monitor at: `https://github.com/etlsurekha01-art/Loan-verification/actions`

### Metrics Tracked

- ✅ Test pass rate
- ✅ Code coverage percentage
- ✅ Build success rate
- ✅ Average build time
- ✅ Security vulnerabilities

### Badges

Add to README.md:

```markdown
![CI/CD](https://github.com/etlsurekha01-art/Loan-verification/workflows/CI/CD%20Pipeline/badge.svg)
![Tests](https://github.com/etlsurekha01-art/Loan-verification/workflows/Pull%20Request%20Tests/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/etlsurekha01-art/Loan-verification)
```

---

## 🆘 Support & Troubleshooting

### Getting Help

1. Check [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review workflow logs in Actions tab
3. Test locally before pushing
4. Check this documentation

### Useful Commands

```bash
# Run tests with verbose output
pytest tests/ -vv --tb=long

# Run specific test file
pytest tests/test_loan.py -v

# Run with coverage and HTML report
pytest --cov=. --cov-report=html --cov-report=term

# Check code formatting
black --check --verbose .

# Auto-format code
black .

# Sort imports
isort .

# Run security scan locally
pip install safety bandit
safety check
bandit -r . -ll
```

---

## 📅 Maintenance

### Regular Tasks

- **Weekly**: Review security scan results
- **Monthly**: Update dependencies
- **Quarterly**: Review and optimize pipeline

### Updating Dependencies

```bash
# Update requirements
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt

# Test after update
pytest tests/ -v
```

---

## 🎯 Future Enhancements

### Planned Improvements

- [ ] Add performance testing
- [ ] Implement staging deployment
- [ ] Add end-to-end tests
- [ ] Setup automatic dependency updates (Dependabot)
- [ ] Add deployment rollback mechanism
- [ ] Implement blue-green deployment
- [ ] Add monitoring and alerting

---

**Last Updated**: February 12, 2026  
**Pipeline Version**: 1.0  
**Maintained by**: Development Team
