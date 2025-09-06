"""
Data processing pipeline for YMCA volunteer data
Handles report generation and milestone tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from volunteer_api_client import VolunteerMattersAPI


class VolunteerDataProcessor:
    """Process volunteer data for reporting and milestone tracking"""
    
    def __init__(self, api_client: VolunteerMattersAPI = None):
        """Initialize with API client"""
        self.api_client = api_client or VolunteerMattersAPI()
        self.milestone_tiers = {
            10: "First Impact",
            25: "Service Star", 
            50: "Commitment Champion",
            100: "Passion In Action Award",
            500: "Guiding Light Award"
        }
    
    def fetch_monthly_data(self, year: int, month: int) -> pd.DataFrame:
        """
        Fetch volunteer data for a specific month
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            DataFrame with volunteer data
        """
        # Calculate date range
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            end_date = f"{year}-{month+1:02d}-01"
            end_date = (pd.to_datetime(end_date) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"Fetching data from {start_date} to {end_date}")
        
        # Get data from API
        history_data = self.api_client.get_all_volunteer_history(
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to DataFrame
        df = self.api_client.volunteer_history_to_dataframe(history_data)
        
        # Remove rows with 0 hours
        if not df.empty and 'credited_hours' in df.columns:
            df = df[df['credited_hours'] > 0]
        
        return df
    
    def fetch_ytd_data(self, year: int, up_to_month: int = None) -> pd.DataFrame:
        """
        Fetch year-to-date volunteer data
        
        Args:
            year: Year (e.g., 2025)
            up_to_month: Month to fetch up to (default: current month)
            
        Returns:
            DataFrame with YTD volunteer data
        """
        if up_to_month is None:
            up_to_month = datetime.now().month
        
        start_date = f"{year}-01-01"
        
        # Calculate end date (first day of next month or end of year)
        if up_to_month == 12:
            end_date = f"{year}-12-31"
        else:
            end_date = f"{year}-{up_to_month+1:02d}-01"
        
        print(f"Fetching YTD data from {start_date} to {end_date}")
        
        # Get data from API
        history_data = self.api_client.get_all_volunteer_history(
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to DataFrame
        df = self.api_client.volunteer_history_to_dataframe(history_data)
        
        # Remove rows with 0 hours
        if not df.empty and 'credited_hours' in df.columns:
            df = df[df['credited_hours'] > 0]
        
        return df
    
    def generate_project_category_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate statistics by project category
        
        Args:
            df: DataFrame with volunteer data
            
        Returns:
            Dictionary with project category statistics
        """
        if df.empty:
            return {
                'hours_by_category': {},
                'volunteers_by_category': {},
                'projects_by_category': {}
            }
        
        stats = {}
        
        # 1. Hours by category (no deduplication)
        if 'project_name' in df.columns and 'credited_hours' in df.columns:
            hours_by_project = df.groupby('project_name')['credited_hours'].sum()
            stats['hours_by_category'] = hours_by_project.to_dict()
        else:
            stats['hours_by_category'] = {}
        
        # 2. Volunteers by category (deduplicated by assignee, project, branch)
        if all(col in df.columns for col in ['contact_id', 'project_name', 'branch_code']):
            volunteers_dedup = df.drop_duplicates(subset=['contact_id', 'project_name', 'branch_code'])
            volunteers_by_project = volunteers_dedup.groupby('project_name')['contact_id'].count()
            stats['volunteers_by_category'] = volunteers_by_project.to_dict()
        else:
            stats['volunteers_by_category'] = {}
        
        # 3. Unique projects count
        if 'project_name' in df.columns and 'branch_code' in df.columns:
            projects_dedup = df.drop_duplicates(subset=['project_name', 'branch_code'])
            unique_projects = projects_dedup['project_name'].nunique()
            stats['total_projects'] = unique_projects
            
            # Projects by category
            project_counts = projects_dedup.groupby('project_name').size()
            stats['projects_by_category'] = project_counts.to_dict()
        else:
            stats['total_projects'] = 0
            stats['projects_by_category'] = {}
        
        return stats
    
    def generate_branch_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate statistics by branch/site
        
        Args:
            df: DataFrame with volunteer data
            
        Returns:
            Dictionary with branch statistics
        """
        if df.empty:
            return {
                'hours_by_branch': {},
                'volunteers_by_branch': {},
                'member_volunteers_by_branch': {}
            }
        
        stats = {}
        
        # 1. Hours by branch (no deduplication)
        if 'branch_name' in df.columns and 'credited_hours' in df.columns:
            hours_by_branch = df.groupby('branch_name')['credited_hours'].sum()
            stats['hours_by_branch'] = hours_by_branch.to_dict()
        else:
            stats['hours_by_branch'] = {}
        
        # 2. Active volunteers by branch (deduplicated by assignee, branch)
        if 'contact_id' in df.columns and 'branch_name' in df.columns:
            volunteers_dedup = df.drop_duplicates(subset=['contact_id', 'branch_name'])
            volunteers_by_branch = volunteers_dedup.groupby('branch_name')['contact_id'].count()
            stats['volunteers_by_branch'] = volunteers_by_branch.to_dict()
        else:
            stats['volunteers_by_branch'] = {}
        
        # 3. Member volunteers by branch
        # Note: This would require member status data from the API
        # For now, returning empty - would need to enhance API client to get contact details
        stats['member_volunteers_by_branch'] = {}
        
        return stats
    
    def identify_milestone_achievements(self, df: pd.DataFrame, 
                                       start_date: str = "2024-01-01") -> pd.DataFrame:
        """
        Identify volunteers who have reached milestone hours
        
        Args:
            df: DataFrame with volunteer data
            start_date: Start date for calculating cumulative hours
            
        Returns:
            DataFrame with milestone achievements
        """
        if df.empty:
            return pd.DataFrame()
        
        # Calculate cumulative hours per volunteer
        volunteer_hours = df.groupby(['contact_id', 'contact_email', 'full_name'])[
            'credited_hours'].sum().reset_index()
        volunteer_hours.columns = ['contact_id', 'email', 'name', 'total_hours']
        
        # Identify milestones reached
        milestones = []
        for _, volunteer in volunteer_hours.iterrows():
            hours = volunteer['total_hours']
            
            for threshold, award_name in self.milestone_tiers.items():
                if hours >= threshold:
                    milestones.append({
                        'contact_id': volunteer['contact_id'],
                        'name': volunteer['name'],
                        'email': volunteer['email'],
                        'total_hours': hours,
                        'milestone_hours': threshold,
                        'award_name': award_name,
                        'milestone_reached': True
                    })
        
        if milestones:
            milestone_df = pd.DataFrame(milestones)
            # Keep only highest milestone per volunteer
            idx = milestone_df.groupby('contact_id')['milestone_hours'].idxmax()
            milestone_df = milestone_df.loc[idx]
            return milestone_df
        
        return pd.DataFrame()
    
    def get_volunteers_approaching_milestones(self, df: pd.DataFrame, 
                                             threshold_percent: float = 0.8) -> pd.DataFrame:
        """
        Identify volunteers approaching milestone thresholds
        
        Args:
            df: DataFrame with volunteer data
            threshold_percent: Percentage of milestone to consider "approaching" (e.g., 0.8 = 80%)
            
        Returns:
            DataFrame with volunteers approaching milestones
        """
        if df.empty:
            return pd.DataFrame()
        
        # Calculate total hours per volunteer
        volunteer_hours = df.groupby(['contact_id', 'contact_email', 'full_name'])[
            'credited_hours'].sum().reset_index()
        volunteer_hours.columns = ['contact_id', 'email', 'name', 'total_hours']
        
        approaching = []
        for _, volunteer in volunteer_hours.iterrows():
            hours = volunteer['total_hours']
            
            # Find next milestone
            for threshold, award_name in self.milestone_tiers.items():
                if hours < threshold:
                    if hours >= threshold * threshold_percent:
                        approaching.append({
                            'contact_id': volunteer['contact_id'],
                            'name': volunteer['name'],
                            'email': volunteer['email'],
                            'current_hours': hours,
                            'next_milestone': threshold,
                            'hours_needed': threshold - hours,
                            'next_award': award_name,
                            'percent_complete': (hours / threshold) * 100
                        })
                    break
        
        if approaching:
            return pd.DataFrame(approaching)
        
        return pd.DataFrame()
    
    def generate_summary_report(self, df: pd.DataFrame, month: str = None) -> Dict:
        """
        Generate comprehensive summary report
        
        Args:
            df: DataFrame with volunteer data
            month: Month label for the report (e.g., "August 2025")
            
        Returns:
            Dictionary with complete report data
        """
        report = {
            'report_month': month or datetime.now().strftime('%B %Y'),
            'data_generated': datetime.now().isoformat(),
            'summary': {},
            'project_stats': {},
            'branch_stats': {},
            'milestones': {}
        }
        
        if not df.empty:
            # Overall summary
            report['summary'] = {
                'total_hours': df['credited_hours'].sum() if 'credited_hours' in df.columns else 0,
                'total_volunteers': df['contact_id'].nunique() if 'contact_id' in df.columns else 0,
                'total_activities': len(df),
                'unique_projects': df['project_name'].nunique() if 'project_name' in df.columns else 0,
                'unique_branches': df['branch_name'].nunique() if 'branch_name' in df.columns else 0
            }
            
            # Project category statistics
            report['project_stats'] = self.generate_project_category_stats(df)
            
            # Branch statistics
            report['branch_stats'] = self.generate_branch_stats(df)
            
            # Milestone achievements
            milestones_df = self.identify_milestone_achievements(df)
            approaching_df = self.get_volunteers_approaching_milestones(df)
            
            report['milestones'] = {
                'achieved': milestones_df.to_dict('records') if not milestones_df.empty else [],
                'approaching': approaching_df.to_dict('records') if not approaching_df.empty else [],
                'total_achieved': len(milestones_df),
                'total_approaching': len(approaching_df)
            }
        
        return report


def generate_monthly_report(year: int = 2025, month: int = 8):
    """
    Generate a monthly volunteer report
    
    Args:
        year: Year for the report
        month: Month for the report (1-12)
    """
    processor = VolunteerDataProcessor()
    
    print(f"Generating report for {datetime(year, month, 1).strftime('%B %Y')}")
    
    # Fetch data
    df = processor.fetch_monthly_data(year, month)
    
    if df.empty:
        print("No data found for the specified period")
        return None
    
    print(f"Found {len(df)} volunteer records")
    
    # Generate report
    report = processor.generate_summary_report(
        df, 
        month=datetime(year, month, 1).strftime('%B %Y')
    )
    
    # Save report to JSON
    report_filename = f"volunteer_report_{year}_{month:02d}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Report saved to {report_filename}")
    
    # Print summary
    print("\n=== Report Summary ===")
    print(f"Total Hours: {report['summary']['total_hours']:,.1f}")
    print(f"Total Volunteers: {report['summary']['total_volunteers']}")
    print(f"Total Activities: {report['summary']['total_activities']}")
    print(f"Milestones Achieved: {report['milestones']['total_achieved']}")
    print(f"Volunteers Approaching Milestones: {report['milestones']['total_approaching']}")
    
    return report


if __name__ == "__main__":
    # Test with sample data generation
    print("Volunteer Data Processor initialized")
    
    # Uncomment to generate a real report:
    # generate_monthly_report(2025, 1)