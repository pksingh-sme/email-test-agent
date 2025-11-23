"""
Email on Acid API Connector for the Email QA Agentic Platform
Handles fetching email proofs and metadata from Email on Acid
"""

import requests
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmailOnAcidConnector:
    def __init__(self):
        self.api_key = os.getenv("EMAIL_ON_ACID_API_KEY")
        self.api_secret = os.getenv("EMAIL_ON_ACID_API_SECRET")
        self.base_url = "https://api.emailonacid.com/v4"
        
        # Check if credentials are available
        if not self.api_key or not self.api_secret:
            raise ValueError("Email on Acid API credentials not found in environment variables")
    
    def get_email_list(self) -> List[Dict[str, Any]]:
        """
        Fetch list of email proofs from Email on Acid
        
        Returns:
            List of email proof metadata
        """
        # This is a placeholder implementation
        # In a real implementation, this would call the Email on Acid API
        # to fetch the list of email proofs
        
        # Return empty list when no credentials are available
        return []
    
    def get_email_details(self, email_id: str) -> Dict[str, Any]:
        """
        Fetch full HTML and metadata for a specific email
        
        Args:
            email_id: Unique identifier for the email
            
        Returns:
            Dict containing email HTML content and metadata
        """
        # This is a placeholder implementation
        # In a real implementation, this would call the Email on Acid API
        # to fetch the HTML content and metadata for a specific email
        
        # Return empty response when no credentials are available
        return {
            "id": email_id,
            "html_content": "",
            "metadata": {
                "subject": "",
                "preheader": "",
                "template_name": "",
                "locale": "en-US",
                "created_at": ""
            },
            "assets": []
        }
    
    def _make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated API request to Email on Acid
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            data: Data to send with request
            
        Returns:
            API response as dictionary
        """
        # Construct full URL
        url = f"{self.base_url}/{endpoint}"
        
        # Set up authentication
        auth = (self.api_key, self.api_secret)
        
        # Make request
        try:
            if method == "GET":
                response = requests.get(url, auth=auth)
            elif method == "POST":
                response = requests.post(url, auth=auth, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Return JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        connector = EmailOnAcidConnector()
        emails = connector.get_email_list()
        print("Email list:", emails)
        
        if emails:
            email_details = connector.get_email_details(emails[0]["id"])
            print("Email details:", email_details)
    except Exception as e:
        print(f"Error: {e}")