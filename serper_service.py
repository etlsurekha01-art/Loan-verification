"""
Serper.dev API integration for company verification.
Provides real web search capabilities for employment verification.
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SerperService:
    """
    Service for interacting with Serper.dev API.
    Provides Google search results for company verification.
    """
    
    SERPER_API_URL = "https://google.serper.dev/search"
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key or self.api_key == "your_serper_api_key_here":
            logger.warning("SERPER_API_KEY not configured - company verification will use simulated results")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Serper API service initialized")
    
    def verify_company(self, company_name: str) -> Dict[str, Any]:
        """
        Verify company legitimacy using Serper.dev API.
        
        Args:
            company_name: Name of the company to verify
            
        Returns:
            Dictionary with verification results
        """
        if not self.enabled:
            return self._simulate_verification(company_name)
        
        try:
            # Construct search query
            query = f"Is {company_name} a legitimate registered company?"
            
            # Make API request
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": 3  # Get top 3 results
            }
            
            logger.info(f"Searching Serper API for: {company_name}")
            response = requests.post(
                self.SERPER_API_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_results(company_name, data)
            else:
                logger.error(f"Serper API error: {response.status_code} - {response.text}")
                return {
                    "verified": False,
                    "confidence": "low",
                    "reason": f"API error: {response.status_code}",
                    "results": []
                }
                
        except requests.exceptions.Timeout:
            logger.error("Serper API timeout")
            return {
                "verified": False,
                "confidence": "low",
                "reason": "API timeout",
                "results": []
            }
        except Exception as e:
            logger.error(f"Serper API exception: {e}")
            return {
                "verified": False,
                "confidence": "low",
                "reason": f"Error: {str(e)}",
                "results": []
            }
    
    def _process_results(self, company_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Serper API results.
        
        Args:
            company_name: Company name
            data: API response data
            
        Returns:
            Processed verification results
        """
        organic_results = data.get("organic", [])
        
        if not organic_results:
            return {
                "verified": False,
                "confidence": "low",
                "reason": "No search results found",
                "results": []
            }
        
        # Extract top 3 results
        results = []
        positive_indicators = 0
        negative_indicators = 0
        
        for result in organic_results[:3]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            results.append({
                "title": title,
                "snippet": snippet,
                "link": link
            })
            
            # Analyze content for verification signals
            content = (title + " " + snippet).lower()
            
            # Positive indicators
            positive_keywords = [
                "official", "website", "company", "corporation", "inc", "ltd",
                "registered", "founded", "headquarters", "employees", "ceo",
                "about us", "careers", "contact", "business"
            ]
            
            # Negative indicators - context-aware patterns
            # Only flag if negative words are directly about the company
            negative_patterns = [
                f"{company_name} scam", f"{company_name} fraud", 
                "is a scam", "is fraud", "is fake", "company is not legitimate",
                "known scam", "fraudulent company"
            ]
            
            for keyword in positive_keywords:
                if keyword in content:
                    positive_indicators += 1
            
            # More careful negative detection - avoid false positives
            # from general help/warning pages
            for pattern in negative_patterns:
                if pattern in content:
                    negative_indicators += 1
            
            # Single negative keywords only count if not in a help/support context
            if not any(word in content for word in ["help", "support", "avoid", "report"]):
                single_negatives = ["scam", "fraud", "fake"]
                for keyword in single_negatives:
                    if keyword in content and keyword not in content.replace(f"{company_name.lower()}", ""):
                        negative_indicators += 1
        
        # Determine verification status
        # Check for official domains and trusted sources
        trusted_domains = ["wikipedia.org", "linkedin.com", "bloomberg.com", "forbes.com", "bbb.org", "sec.gov"]
        has_official_site = any(company_name.lower().replace(" ", "") in r.get("link", "").lower() for r in results)
        has_trusted_source = any(any(domain in r.get("link", "") for domain in trusted_domains) for r in results)
        
        # More strict: require at least 5 positive indicators for high confidence
        # Also check if results are actually about checking scams vs company info
        scam_checking_keywords = ["scamadviser", "is scam", "check if", "legit or scam", "reported scam", "fraud database"]
        is_scam_checking = sum(1 for r in results if any(k in (r.get("title", "") + r.get("snippet", "")).lower() for k in scam_checking_keywords))
        
        if negative_indicators > 2:
            verified = False
            confidence = "high"
            reason = "Negative indicators found in search results"
        elif has_official_site or has_trusted_source:
            # If we found the company's official website or a trusted source, verify it
            verified = True
            confidence = "high"
            reason = "Company appears legitimate based on search results"
        elif is_scam_checking >= 2:
            # If most results are about checking if it's a scam, it's suspicious
            verified = False
            confidence = "low"
            reason = "Company verification inconclusive - insufficient legitimate sources"
        elif positive_indicators >= 7:
            verified = True
            confidence = "high"
            reason = "Company appears legitimate based on search results"
        elif positive_indicators >= 4:
            verified = True
            confidence = "medium"
            reason = "Some positive indicators found"
        else:
            verified = False
            confidence = "low"
            reason = "Insufficient verification information"
        
        return {
            "verified": verified,
            "confidence": confidence,
            "reason": reason,
            "results": results,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators
        }
    
    def _simulate_verification(self, company_name: str) -> Dict[str, Any]:
        """
        Simulate verification when API is not available.
        
        Args:
            company_name: Company name
            
        Returns:
            Simulated verification results
        """
        logger.warning(f"Using simulated verification for {company_name}")
        
        # Known legitimate companies
        legitimate_companies = [
            "google", "microsoft", "apple", "amazon", "meta", "facebook",
            "netflix", "tesla", "nvidia", "intel", "ibm", "oracle",
            "salesforce", "adobe", "cisco", "vmware"
        ]
        
        company_lower = company_name.lower()
        is_known = any(comp in company_lower for comp in legitimate_companies)
        
        if is_known:
            return {
                "verified": True,
                "confidence": "simulated",
                "reason": "Known company (simulated - API key not configured)",
                "results": [
                    {
                        "title": f"{company_name} - Official Website",
                        "snippet": f"{company_name} is a well-known technology company...",
                        "link": f"https://www.{company_name.lower().replace(' ', '')}.com"
                    }
                ]
            }
        else:
            return {
                "verified": False,
                "confidence": "simulated",
                "reason": "Unable to verify (simulated - API key not configured)",
                "results": []
            }


# Global service instance
_serper_service: Optional[SerperService] = None


def get_serper_service() -> SerperService:
    """
    Get or create global Serper service instance.
    
    Returns:
        SerperService instance
    """
    global _serper_service
    if _serper_service is None:
        _serper_service = SerperService()
    return _serper_service
