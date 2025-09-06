"""
YMCA Volunteer Management Application
Main application for fetching, processing, and visualizing volunteer data
"""

import sys
import argparse
from datetime import datetime
import json
import pandas as pd
from volunteer_api_client import VolunteerMattersAPI
from volunteer_data_processor import VolunteerDataProcessor
from dashboard_generator import DashboardGenerator, generate_dashboard


# Hardcoded credentials as requested
API_KEY = "62lJN9CLNQbuVag36vFSmDg"
API_SECRET = "oRBbayCJRE2fdJyqKfs9Axw"
CUSTOMER_CODE = "cincinnatiymca"


def test_connection():
    """Test API connection"""
    print("Testing VolunteerMatters API connection...")
    
    client = VolunteerMattersAPI(
        api_key=API_KEY,
        api_secret=API_SECRET,
        customer_code=CUSTOMER_CODE
    )
    
    try:
        branches = client.get_branches()
        print(f"Connection successful! Found {branches.get('totalItems', 0)} branches.")
        
        if 'items' in branches and branches['items']:
            print("\nAvailable branches:")
            for branch in branches['items'][:10]:
                print(f"  - {branch.get('name')} (Code: {branch.get('code')})")
        
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def generate_monthly_report(year: int, month: int, output_format: str = "all"):
    """
    Generate monthly volunteer report
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        output_format: Output format (json, html, excel, or all)
    """
    print(f"\nGenerating report for {datetime(year, month, 1).strftime('%B %Y')}...")
    
    # Initialize API client and processor
    client = VolunteerMattersAPI(
        api_key=API_KEY,
        api_secret=API_SECRET,
        customer_code=CUSTOMER_CODE
    )
    processor = VolunteerDataProcessor(api_client=client)
    
    # Fetch data
    print("Fetching volunteer data from API...")
    df = processor.fetch_monthly_data(year, month)
    
    if df.empty:
        print("No data found for the specified period")
        return None
    
    print(f"Found {len(df)} volunteer records")
    print(f"Total hours: {df['credited_hours'].sum():,.1f}")
    print(f"Unique volunteers: {df['contact_id'].nunique()}")
    
    # Generate report
    print("Processing data...")
    report = processor.generate_summary_report(
        df,
        month=datetime(year, month, 1).strftime('%B %Y')
    )
    
    # Save outputs based on format
    outputs = []
    
    if output_format in ["json", "all"]:
        json_filename = f"volunteer_report_{year}_{month:02d}.json"
        with open(json_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"JSON report saved to {json_filename}")
        outputs.append(json_filename)
    
    if output_format in ["html", "excel", "all"]:
        generator = DashboardGenerator()
        
        if output_format in ["html", "all"]:
            html = generator.create_dashboard_html(report)
            html_filename = f"dashboard_{year}_{month:02d}.html"
            with open(html_filename, 'w') as f:
                f.write(html)
            print(f"HTML dashboard saved to {html_filename}")
            outputs.append(html_filename)
        
        if output_format in ["excel", "all"]:
            excel_filename = generator.export_to_excel(
                report,
                f"volunteer_report_{year}_{month:02d}.xlsx"
            )
            outputs.append(excel_filename)
    
    return outputs


def track_milestones(start_date: str = "2024-01-01", output_file: str = "milestones.csv"):
    """
    Track volunteer milestones from a start date
    
    Args:
        start_date: Start date for tracking (YYYY-MM-DD)
        output_file: Output CSV filename
    """
    print(f"\nTracking milestones from {start_date}...")
    
    # Initialize API client and processor
    client = VolunteerMattersAPI(
        api_key=API_KEY,
        api_secret=API_SECRET,
        customer_code=CUSTOMER_CODE
    )
    processor = VolunteerDataProcessor(api_client=client)
    
    # Fetch all data from start date
    print("Fetching volunteer history...")
    history = client.get_all_volunteer_history(start_date=start_date)
    df = client.volunteer_history_to_dataframe(history)
    
    if df.empty:
        print("No data found")
        return None
    
    # Remove zero hours
    df = df[df['credited_hours'] > 0]
    
    print(f"Found {len(df)} volunteer records")
    print(f"Unique volunteers: {df['contact_id'].nunique()}")
    
    # Identify milestones
    milestones_df = processor.identify_milestone_achievements(df, start_date)
    approaching_df = processor.get_volunteers_approaching_milestones(df)
    
    print(f"\nMilestone Summary:")
    print(f"Volunteers who achieved milestones: {len(milestones_df)}")
    print(f"Volunteers approaching milestones: {len(approaching_df)}")
    
    # Save milestone achievements
    if not milestones_df.empty:
        milestones_df.to_csv(output_file, index=False)
        print(f"Milestone achievements saved to {output_file}")
        
        # Show breakdown by milestone level
        print("\nMilestones achieved:")
        for award in milestones_df['award_name'].value_counts().items():
            print(f"  - {award[0]}: {award[1]} volunteers")
    
    # Save approaching milestones
    if not approaching_df.empty:
        approaching_file = output_file.replace('.csv', '_approaching.csv')
        approaching_df.to_csv(approaching_file, index=False)
        print(f"Approaching milestones saved to {approaching_file}")
    
    return milestones_df, approaching_df


def fetch_raw_data(start_date: str, end_date: str = None, output_file: str = "raw_volunteer_data.csv"):
    """
    Fetch raw volunteer data and save to CSV
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), optional
        output_file: Output CSV filename
    """
    print(f"\nFetching raw data from {start_date}" + (f" to {end_date}" if end_date else ""))
    
    # Initialize API client
    client = VolunteerMattersAPI(
        api_key=API_KEY,
        api_secret=API_SECRET,
        customer_code=CUSTOMER_CODE
    )
    
    # Fetch data
    print("Fetching volunteer history from API...")
    history = client.get_all_volunteer_history(start_date=start_date, end_date=end_date)
    
    if not history:
        print("No data found")
        return None
    
    # Convert to DataFrame
    df = client.volunteer_history_to_dataframe(history)
    
    # Remove zero hours as per requirements
    df = df[df['credited_hours'] > 0]
    
    print(f"Found {len(df)} records with non-zero hours")
    print(f"Date range: {df['volunteer_date'].min()} to {df['volunteer_date'].max()}")
    print(f"Total hours: {df['credited_hours'].sum():,.1f}")
    print(f"Unique volunteers: {df['contact_id'].nunique()}")
    print(f"Unique projects: {df['project_name'].nunique()}")
    print(f"Unique branches: {df['branch_name'].nunique()}")
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\nData saved to {output_file}")
    
    return df


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='YMCA Volunteer Management System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test connection command
    parser_test = subparsers.add_parser('test', help='Test API connection')
    
    # Generate report command
    parser_report = subparsers.add_parser('report', help='Generate monthly report')
    parser_report.add_argument('--year', type=int, default=datetime.now().year,
                              help='Year (default: current year)')
    parser_report.add_argument('--month', type=int, default=datetime.now().month,
                              help='Month 1-12 (default: current month)')
    parser_report.add_argument('--format', choices=['json', 'html', 'excel', 'all'],
                              default='all', help='Output format')
    
    # Track milestones command
    parser_milestones = subparsers.add_parser('milestones', help='Track volunteer milestones')
    parser_milestones.add_argument('--start-date', default='2024-01-01',
                                   help='Start date (YYYY-MM-DD)')
    parser_milestones.add_argument('--output', default='milestones.csv',
                                   help='Output CSV file')
    
    # Fetch raw data command
    parser_fetch = subparsers.add_parser('fetch', help='Fetch raw volunteer data')
    parser_fetch.add_argument('--start-date', required=True,
                             help='Start date (YYYY-MM-DD)')
    parser_fetch.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser_fetch.add_argument('--output', default='raw_volunteer_data.csv',
                             help='Output CSV file')
    
    args = parser.parse_args()
    
    if not args.command:
        print("YMCA Volunteer Management System")
        print("\nUsage examples:")
        print("  python ymca_volunteer_app.py test                    # Test API connection")
        print("  python ymca_volunteer_app.py report --year 2025 --month 1")
        print("  python ymca_volunteer_app.py milestones --start-date 2024-01-01")
        print("  python ymca_volunteer_app.py fetch --start-date 2025-01-01")
        print("\nUse -h for more options")
        return
    
    # Execute command
    if args.command == 'test':
        test_connection()
    
    elif args.command == 'report':
        generate_monthly_report(args.year, args.month, args.format)
    
    elif args.command == 'milestones':
        track_milestones(args.start_date, args.output)
    
    elif args.command == 'fetch':
        fetch_raw_data(args.start_date, args.end_date, args.output)


if __name__ == "__main__":
    main()