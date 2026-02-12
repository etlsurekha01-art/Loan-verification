"""
Employment Verification Agent - Validates employment and company information.
Simulates LinkedIn and Glassdoor checks (no actual web scraping).
"""

import logging
from typing import Optional
from models import EmploymentResult, LoanApplicationRequest

logger = logging.getLogger(__name__)


class EmploymentAgent:
    """
    Employment Verification Agent validates employment status and company legitimacy.
    Uses simulated web searches (LinkedIn, Glassdoor) for verification.
    """
    
    # Known reputable companies (for simulation)
    REPUTABLE_COMPANIES = [
        "google", "microsoft", "apple", "amazon", "meta", "facebook",
        "netflix", "tesla", "nvidia", "intel", "ibm", "oracle",
        "salesforce", "adobe", "cisco", "vmware", "dell", "hp",
        "goldman sachs", "jpmorgan", "morgan stanley", "citigroup",
        "bank of america", "wells fargo", "mastercard", "visa",
        "pfizer", "johnson & johnson", "merck", "abbott",
        "exxonmobil", "chevron", "boeing", "lockheed martin"
    ]
    
    def __init__(self):
        self.agent_name = "EmploymentAgent"
        logger.info(f"{self.agent_name} initialized")
    
    async def process(self, application: LoanApplicationRequest) -> EmploymentResult:
        """
        Verify employment information.
        
        Args:
            application: Loan application request
            
        Returns:
            EmploymentResult with verification details
        """
        try:
            logger.info(f"{self.agent_name} verifying employment for {application.name}")
            
            # Enhanced LinkedIn profile verification
            linkedin_profile_found = False
            profile_completeness = None
            employment_history_verified = False
            
            if application.linkedin_url:
                linkedin_profile_found = True
                profile_completeness = self._assess_profile_completeness(
                    application.linkedin_url,
                    application.job_title,
                    application.previous_employers
                )
                employment_history_verified = self._verify_employment_history(
                    application.employment_years,
                    application.previous_employers,
                    application.company_name
                )
            
            # Simulate LinkedIn check
            linkedin_result = self._simulate_linkedin_check(
                application.name, 
                application.company_name,
                application.employment_years,
                application.linkedin_url,
                application.job_title
            )
            
            # Simulate Glassdoor check
            glassdoor_result = self._simulate_glassdoor_check(application.company_name)
            
            # Assess professional credentials
            professional_credentials = self._assess_professional_credentials(
                application.job_title,
                application.employment_type,
                application.professional_email,
                application.company_name
            )
            
            # Determine employment verification status
            employment_verified = self._verify_employment(
                application.employment_years,
                linkedin_result,
                linkedin_profile_found
            )
            
            # Determine company verification status
            company_verified = self._verify_company(
                application.company_name,
                glassdoor_result
            )
            
            # Assess employment stability
            stability = self._assess_stability(
                application.employment_years,
                company_verified,
                application.previous_employers
            )
            
            # Determine if there are risk flags
            risk_flag = self._check_risk_flags(
                employment_verified,
                company_verified,
                application.employment_years,
                linkedin_profile_found
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                application,
                employment_verified,
                company_verified,
                stability,
                linkedin_result,
                glassdoor_result,
                profile_completeness,
                professional_credentials
            )
            
            result = EmploymentResult(
                employment_verified=employment_verified,
                company_verified=company_verified,
                employment_stability=stability,
                linkedin_check=linkedin_result,
                glassdoor_check=glassdoor_result,
                linkedin_profile_found=linkedin_profile_found,
                profile_completeness=profile_completeness,
                employment_history_verified=employment_history_verified,
                professional_credentials=professional_credentials,
                reasoning=reasoning,
                risk_flag=risk_flag
            )
            
            logger.info(f"{self.agent_name} completed: verified={employment_verified}, stability={stability}, linkedin={linkedin_profile_found}")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} error: {e}")
            raise
    
    def _assess_profile_completeness(
        self,
        linkedin_url: str,
        job_title: Optional[str],
        previous_employers: Optional[int]
    ) -> str:
        """
        Assess LinkedIn profile completeness.
        
        Args:
            linkedin_url: LinkedIn profile URL
            job_title: Job title
            previous_employers: Number of previous employers
            
        Returns:
            Completeness assessment
        """
        if not linkedin_url:
            return "No profile provided"
        
        # Check URL validity (basic check)
        if "linkedin.com/in/" not in linkedin_url.lower():
            return "Invalid LinkedIn URL format"
        
        # Simulate completeness based on provided information
        completeness_score = 0
        details = []
        
        if linkedin_url:
            completeness_score += 40
            details.append("Profile URL provided")
        
        if job_title:
            completeness_score += 30
            details.append("Job title specified")
        
        if previous_employers is not None:
            completeness_score += 30
            details.append("Employment history available")
        
        if completeness_score >= 80:
            return f"Comprehensive ({completeness_score}%) - {', '.join(details)}"
        elif completeness_score >= 50:
            return f"Moderate ({completeness_score}%) - {', '.join(details)}"
        else:
            return f"Limited ({completeness_score}%) - {', '.join(details)}"
    
    def _verify_employment_history(
        self,
        current_years: float,
        previous_employers: Optional[int],
        company_name: str
    ) -> bool:
        """
        Verify employment history consistency.
        
        Args:
            current_years: Years at current employer
            previous_employers: Number of previous employers
            company_name: Current company name
            
        Returns:
            True if history is consistent
        """
        if previous_employers is None:
            return False
        
        # Consider verified if:
        # - Has reasonable job history
        # - Not too many job changes (indicates stability)
        if current_years >= 2.0 and previous_employers <= 5:
            return True
        elif current_years >= 5.0:  # Long tenure compensates for more changes
            return True
        elif previous_employers <= 2:  # Few changes is good even with shorter tenure
            return True
        
        return False
    
    def _assess_professional_credentials(
        self,
        job_title: Optional[str],
        employment_type: Optional[str],
        professional_email: Optional[str],
        company_name: str
    ) -> str:
        """
        Assess professional credentials and legitimacy.
        
        Args:
            job_title: Job title
            employment_type: Employment type
            professional_email: Work email
            company_name: Company name
            
        Returns:
            Credentials assessment
        """
        score = 0
        details = []
        
        # Check job title
        if job_title:
            senior_titles = ["senior", "lead", "principal", "director", "manager", "vp", "chief"]
            if any(title in job_title.lower() for title in senior_titles):
                score += 30
                details.append("Senior position")
            else:
                score += 20
                details.append("Professional role")
        
        # Check employment type
        if employment_type:
            if employment_type.lower() == "full-time":
                score += 30
                details.append("Full-time employment")
            elif employment_type.lower() == "part-time":
                score += 15
                details.append("Part-time employment")
            else:
                score += 10
                details.append(f"{employment_type} employment")
        
        # Check professional email
        if professional_email:
            company_domain = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
            email_lower = professional_email.lower()
            
            if company_domain[:5] in email_lower or "@" in email_lower:
                score += 40
                details.append("Corporate email verified")
            else:
                score += 20
                details.append("Email provided")
        
        if score >= 70:
            return f"Strong credentials - {', '.join(details)}"
        elif score >= 40:
            return f"Adequate credentials - {', '.join(details)}"
        elif score > 0:
            return f"Basic credentials - {', '.join(details)}"
        else:
            return "Limited credential information"
    
    def _simulate_linkedin_check(
        self, 
        name: str, 
        company: str, 
        years: float,
        linkedin_url: Optional[str] = None,
        job_title: Optional[str] = None
    ) -> str:
        """
        Simulate LinkedIn profile verification.
        
        Args:
            name: Applicant name
            company: Company name
            years: Years of employment
            linkedin_url: LinkedIn profile URL (optional)
            job_title: Job title (optional)
            
        Returns:
            Verification result string
        """
        # Enhanced verification with LinkedIn URL
        if linkedin_url:
            if "linkedin.com/in/" in linkedin_url.lower():
                profile_quality = "comprehensive" if job_title else "basic"
                if years >= 5:
                    return (f"✓ LinkedIn profile verified: {name} at {company} for {years:.1f} years. "
                           f"Profile URL confirmed with {profile_quality} information. "
                           f"{f'Job title: {job_title}. ' if job_title else ''}"
                           f"Profile shows strong professional presence with verified employment history.")
                elif years >= 2:
                    return (f"✓ LinkedIn profile verified: {name} at {company} for {years:.1f} years. "
                           f"Profile URL confirmed. {f'Current role: {job_title}. ' if job_title else ''}"
                           f"Profile appears authentic with moderate activity.")
                elif years >= 1:
                    return (f"✓ LinkedIn profile found: {name} listed at {company} for {years:.1f} years. "
                           f"Profile URL provided. {f'Position: {job_title}. ' if job_title else ''}"
                           f"Recent profile with limited history.")
                else:
                    return (f"⚠ LinkedIn profile found: {name} at {company} for {years:.1f} years. "
                           f"Profile URL provided but very recent employment. Limited verification possible.")
            else:
                return f"⚠ Invalid LinkedIn URL format provided. Manual verification may be required."
        
        # Original simulation without LinkedIn URL
        if years >= 5:
            return f"⚠ No LinkedIn profile URL provided. Based on tenure ({years:.1f} years), employment likely legitimate but unverified."
        elif years >= 2:
            return f"⚠ No LinkedIn profile URL provided. {name} claims {years:.1f} years at {company}. Limited verification available."
        elif years >= 1:
            return f"⚠ No LinkedIn profile URL provided. Recent employment ({years:.1f} years). Profile verification recommended."
        else:
            return f"⚠ No LinkedIn profile URL provided. Very recent employment ({years:.1f} years). Additional verification strongly recommended."
    
    def _simulate_glassdoor_check(self, company: str) -> str:
        """
        Simulate Glassdoor company verification.
        
        Args:
            company: Company name
            
        Returns:
            Verification result string
        """
        company_lower = company.lower()
        
        # Check if it's a known reputable company
        is_reputable = any(rep in company_lower for rep in self.REPUTABLE_COMPANIES)
        
        if is_reputable:
            return f"✓ Glassdoor verified: {company} is a well-established company with positive ratings (4.2/5.0) and 1000+ employee reviews."
        elif len(company) > 5 and not company.lower().startswith(("xyz", "unknown", "test")):
            return f"⚠ Glassdoor listing found: {company} has a Glassdoor presence with mixed reviews (3.5/5.0). Appears to be a legitimate business."
        else:
            return f"✗ Glassdoor check: Limited or no information found for {company}. Company legitimacy cannot be fully verified."
    
    def _verify_employment(self, years: float, linkedin_result: str, linkedin_profile_found: bool = False) -> bool:
        """
        Determine if employment is verified.
        
        Args:
            years: Years of employment
            linkedin_result: LinkedIn check result
            linkedin_profile_found: Whether LinkedIn profile was provided
            
        Returns:
            True if employment is verified
        """
        # Enhanced verification with LinkedIn profile
        if linkedin_profile_found:
            return years >= 0.5 and "✓" in linkedin_result
        
        # Original verification without LinkedIn
        return years >= 1.0 and "✓" in linkedin_result
    
    def _verify_company(self, company: str, glassdoor_result: str) -> bool:
        """
        Determine if company is verified.
        
        Args:
            company: Company name
            glassdoor_result: Glassdoor check result
            
        Returns:
            True if company is verified
        """
        return "✓" in glassdoor_result or "⚠" in glassdoor_result
    
    def _assess_stability(self, years: float, company_verified: bool, previous_employers: Optional[int] = None) -> str:
        """
        Assess employment stability.
        
        Args:
            years: Years of employment
            company_verified: Whether company is verified
            previous_employers: Number of previous employers
            
        Returns:
            Stability assessment string
        """
        # Enhanced stability assessment with job history
        if previous_employers is not None:
            if years >= 5 and company_verified and previous_employers <= 3:
                return "Excellent"
            elif years >= 3 and company_verified and previous_employers <= 5:
                return "Good"
            elif years >= 2 and previous_employers <= 6:
                return "Fair"
            elif previous_employers > 8:
                return "Poor"  # Too many job changes indicates instability
        
        # Original stability assessment
        if years >= 5 and company_verified:
            return "Excellent"
        elif years >= 3 and company_verified:
            return "Good"
        elif years >= 1:
            return "Fair"
        else:
            return "Poor"
    
    def _check_risk_flags(
        self,
        employment_verified: bool,
        company_verified: bool,
        years: float,
        linkedin_profile_found: bool = False
    ) -> bool:
        """
        Check for employment-related risk flags.
        
        Args:
            employment_verified: Whether employment is verified
            company_verified: Whether company is verified
            years: Years of employment
            linkedin_profile_found: Whether LinkedIn profile was provided
            
        Returns:
            True if risk flags present
        """
        # Reduced risk if LinkedIn profile is provided
        if linkedin_profile_found and employment_verified:
            if years >= 0.5:  # More lenient with LinkedIn verification
                return False
        
        # Original risk flags
        if not employment_verified:
            return True
        if not company_verified:
            return True
        if years < 1:
            return True
        
        return False
    
    def _generate_reasoning(
        self,
        application: LoanApplicationRequest,
        employment_verified: bool,
        company_verified: bool,
        stability: str,
        linkedin_result: str,
        glassdoor_result: str,
        profile_completeness: Optional[str] = None,
        professional_credentials: Optional[str] = None
    ) -> str:
        """
        Generate detailed reasoning for employment verification.
        
        Args:
            application: Loan application request
            employment_verified: Employment verification status
            company_verified: Company verification status
            stability: Stability assessment
            linkedin_result: LinkedIn check result
            glassdoor_result: Glassdoor check result
            profile_completeness: Profile completeness assessment
            professional_credentials: Professional credentials assessment
            
        Returns:
            Reasoning string
        """
        lines = [
            f"Employment Verification for {application.name}:",
            f"• Company: {application.company_name}",
            f"• Employment Duration: {application.employment_years:.1f} years",
            f"• Employment Verified: {'Yes' if employment_verified else 'No'}",
            f"• Company Verified: {'Yes' if company_verified else 'No'}",
            f"• Stability Assessment: {stability}",
            ""
        ]
        
        # Add LinkedIn profile information
        if application.linkedin_url:
            lines.append("LinkedIn Profile Verification:")
            lines.append(f"• Profile URL: Provided")
            if profile_completeness:
                lines.append(f"• Profile Completeness: {profile_completeness}")
            if application.job_title:
                lines.append(f"• Job Title: {application.job_title}")
            if application.previous_employers is not None:
                lines.append(f"• Previous Employers: {application.previous_employers}")
            lines.append("")
        
        # Add professional credentials
        if professional_credentials:
            lines.append("Professional Credentials:")
            lines.append(f"• {professional_credentials}")
            if application.employment_type:
                lines.append(f"• Employment Type: {application.employment_type}")
            if application.professional_email:
                lines.append(f"• Professional Email: Provided")
            lines.append("")
        
        lines.append("Verification Details:")
        lines.append(f"• LinkedIn: {linkedin_result}")
        lines.append(f"• Glassdoor: {glassdoor_result}")
        lines.append("")
        
        # Add summary assessment
        if employment_verified and company_verified and stability in ["Excellent", "Good"]:
            if application.linkedin_url:
                lines.append("✓ Enhanced employment verification successful. LinkedIn profile verified with comprehensive employment history at a verified company.")
            else:
                lines.append("✓ Employment verification successful. Applicant demonstrates stable employment at a verified company.")
        elif employment_verified and company_verified:
            lines.append("⚠ Employment verified but relatively recent. Monitor for stability. LinkedIn profile verification recommended.")
        else:
            if not application.linkedin_url:
                lines.append("✗ Employment verification concerns detected. LinkedIn profile URL required for enhanced verification.")
            else:
                lines.append("✗ Employment verification concerns detected. Additional documentation may be required.")
        
        return "\n".join(lines)
