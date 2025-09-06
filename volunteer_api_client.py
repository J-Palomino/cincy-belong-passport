"""
VolunteerMatters API Client for YMCA Cincinnati
Handles authentication and data retrieval from the VolunteerMatters API
"""

import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VolunteerMattersAPI:
    """Client for interacting with the VolunteerMatters API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, customer_code: str = None):
        """
        Initialize the API client
        
        Args:
            api_key: API Key from VolunteerMatters
            api_secret: API Secret from VolunteerMatters  
            customer_code: Customer code for the organization
        """
        self.api_key = api_key or os.getenv('VM_API_KEY', '62lJN9CLNQbuVag36vFSmDg')
        self.api_secret = api_secret or os.getenv('VM_API_SECRET', 'oRBbayCJRE2fdJyqKfs9Axw')
        self.customer_code = customer_code or os.getenv('VM_CUSTOMER_CODE', 'cincinnatiymca')
        self.base_url = "https://api.volunteermatters.io/api/v2"
        self.auth = HTTPBasicAuth(self.api_key, self.api_secret)
        self.headers = {
            'X-VM-Customer-Code': self.customer_code,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        Make an authenticated request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def get_volunteer_history(self, 
                            start_date: str = None,
                            end_date: str = None,
                            page_size: int = 1000,
                            page_index: int = 0,
                            branch_codes: str = None,
                            tag_codes: str = None) -> Dict:
        """
        Get volunteer history records
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            page_size: Number of records per page
            page_index: Page number (0-based)
            branch_codes: Comma-separated branch codes
            tag_codes: Comma-separated tag codes
            
        Returns:
            Paginated volunteer history data
        """
        params = {
            'pageSize': page_size,
            'pageIndex': page_index
        }
        
        # Add date filters if provided
        if start_date and end_date:
            params['volunteerDateSpecs'] = f"ge:{start_date},le:{end_date}"
        elif start_date:
            params['volunteerDateSpecs'] = f"ge:{start_date}"
        elif end_date:
            params['volunteerDateSpecs'] = f"le:{end_date}"
        
        if branch_codes:
            params['branchCodes'] = branch_codes
        
        if tag_codes:
            params['tagCodes'] = tag_codes
            
        return self._make_request('GET', '/volunteerHistory', params=params)
    
    def get_all_volunteer_history(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get all volunteer history records (handles pagination)
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of all volunteer history records
        """
        all_records = []
        page_index = 0
        
        while True:
            data = self.get_volunteer_history(
                start_date=start_date,
                end_date=end_date,
                page_index=page_index
            )
            
            if 'items' in data:
                all_records.extend(data['items'])
                
                # Check if there are more pages
                if page_index >= data.get('totalPages', 1) - 1:
                    break
                page_index += 1
            else:
                break
                
        return all_records
    
    def get_contacts(self, page_size: int = 1000, page_index: int = 0, status_codes: str = None) -> Dict:
        """
        Get contact records
        
        Args:
            page_size: Number of records per page
            page_index: Page number (0-based)
            status_codes: Filter by status (e.g., "Active")
            
        Returns:
            Paginated contact data
        """
        params = {
            'pageSize': page_size,
            'pageIndex': page_index
        }
        
        if status_codes:
            params['statusCodes'] = status_codes
            
        return self._make_request('GET', '/contacts', params=params)
    
    def get_projects(self, page_size: int = 1000, page_index: int = 0, branch_codes: str = None) -> Dict:
        """
        Get project records
        
        Args:
            page_size: Number of records per page
            page_index: Page number (0-based)
            branch_codes: Filter by branch codes
            
        Returns:
            Paginated project data
        """
        params = {
            'pageSize': page_size,
            'pageIndex': page_index
        }
        
        if branch_codes:
            params['branchCodes'] = branch_codes
            
        return self._make_request('GET', '/projects', params=params)
    
    def get_branches(self) -> Dict:
        """
        Get all branch records
        
        Returns:
            Branch data
        """
        return self._make_request('GET', '/branches')
    
    def get_project_tags(self) -> Dict:
        """
        Get all project tags
        
        Returns:
            Project tag data
        """
        return self._make_request('GET', '/projects/tags')
    
    def volunteer_history_to_dataframe(self, history_data: List[Dict]) -> pd.DataFrame:
        """
        Convert volunteer history data to a pandas DataFrame
        
        Args:
            history_data: List of volunteer history records
            
        Returns:
            DataFrame with processed volunteer data
        """
        if not history_data:
            return pd.DataFrame()
        
        # Flatten the nested structure
        flattened_data = []
        
        for record in history_data:
            flat_record = {
                'volunteer_date': record.get('volunteerDate'),
                'credited_hours': record.get('creditedHours', 0),
                'volunteer_comments': record.get('volunteerComments', ''),
                'manually_reported': record.get('manuallyReported', False)
            }
            
            # Extract assignment info
            if 'assignment' in record and record['assignment']:
                assignment = record['assignment']
                flat_record['assignment_id'] = assignment.get('id')
                flat_record['pledge_count'] = assignment.get('pledgeCount', 0)
                flat_record['delivered_count'] = assignment.get('deliveredCount', 0)
                
                # Extract contact info
                if 'contact' in assignment and assignment['contact']:
                    contact = assignment['contact']
                    flat_record['contact_id'] = contact.get('id')
                    flat_record['contact_external_id'] = contact.get('externalId')
                    flat_record['contact_email'] = contact.get('email')
                    
                    # Extract contact name
                    if 'name' in contact and contact['name']:
                        name = contact['name']
                        flat_record['first_name'] = name.get('first', '')
                        flat_record['last_name'] = name.get('last', '')
                        flat_record['full_name'] = f"{name.get('first', '')} {name.get('last', '')}"
                
                # Extract need info
                if 'need' in assignment and assignment['need']:
                    need = assignment['need']
                    flat_record['need_id'] = need.get('id')
                    flat_record['need_type'] = need.get('needType')
                    flat_record['need_name'] = need.get('name')
                    flat_record['start_date'] = need.get('startDateTime')
                    flat_record['end_date'] = need.get('endDateTime')
                    
                    # Extract project info
                    if 'project' in need and need['project']:
                        project = need['project']
                        flat_record['project_id'] = project.get('id')
                        flat_record['project_name'] = project.get('name')
                        
                        # Extract branch info
                        if 'branch' in project and project['branch']:
                            branch = project['branch']
                            flat_record['branch_id'] = branch.get('id')
                            flat_record['branch_code'] = branch.get('code')
                            flat_record['branch_name'] = branch.get('name')
            
            flattened_data.append(flat_record)
        
        df = pd.DataFrame(flattened_data)
        
        # Convert date strings to datetime
        if 'volunteer_date' in df.columns:
            df['volunteer_date'] = pd.to_datetime(df['volunteer_date'])
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'])
        if 'end_date' in df.columns:
            df['end_date'] = pd.to_datetime(df['end_date'])
        
        return df


def test_connection():
    """Test the API connection and print basic info"""
    client = VolunteerMattersAPI()
    
    print("Testing VolunteerMatters API connection...")
    print(f"Customer Code: {client.customer_code}")
    
    try:
        # Test getting branches
        branches = client.get_branches()
        print(f"\nSuccessfully connected! Found {branches.get('totalItems', 0)} branches.")
        
        # Show first few branches
        if 'items' in branches and branches['items']:
            print("\nBranches:")
            for branch in branches['items'][:5]:
                print(f"  - {branch.get('name')} (Code: {branch.get('code')})")
        
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    if test_connection():
        print("\nAPI client is ready to use!")