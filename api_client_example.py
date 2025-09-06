"""
Example client for the YMCA Volunteer API
Shows how to query the REST API endpoints
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000/api"


def test_api():
    """Test various API endpoints"""
    
    print("=" * 50)
    print("YMCA Volunteer API Client Examples")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Testing API health...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✓ API is healthy")
        print(f"   Response: {response.json()}")
    
    # 2. Get branches
    print("\n2. Fetching branches...")
    response = requests.get(f"{BASE_URL}/branches")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            branches = data['data'].get('items', [])
            print(f"✓ Found {len(branches)} branches")
            for branch in branches[:3]:
                print(f"   - {branch.get('name')} (Code: {branch.get('code')})")
    
    # 3. Get monthly report
    print("\n3. Getting January 2025 monthly report...")
    response = requests.get(f"{BASE_URL}/report/monthly/2025/1?format=summary")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            summary = data['data']
            print("✓ Monthly report summary:")
            print(f"   - Total Hours: {summary.get('total_hours', 0):,.1f}")
            print(f"   - Total Volunteers: {summary.get('total_volunteers', 0)}")
            print(f"   - Unique Projects: {summary.get('unique_projects', 0)}")
    
    # 4. Get milestones
    print("\n4. Checking milestone achievements...")
    response = requests.get(f"{BASE_URL}/milestones?start_date=2024-01-01")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            milestones = data['data']
            print(f"✓ Milestone summary:")
            print(f"   - Volunteers who achieved milestones: {milestones['summary']['total_achieved']}")
            print(f"   - Volunteers approaching milestones: {milestones['summary']['total_approaching']}")
            
            # Show some achievements
            if milestones['achieved']:
                print("\n   Recent achievements:")
                for volunteer in milestones['achieved'][:3]:
                    print(f"   - {volunteer['name']}: {volunteer['award_name']} ({volunteer['total_hours']:.1f} hours)")
    
    # 5. Get volunteer hours grouped by branch
    print("\n5. Getting volunteer hours by branch...")
    response = requests.get(f"{BASE_URL}/volunteers/hours?group_by=branch&start_date=2025-01-01")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            branches = data['data']
            print(f"✓ Found data for {len(branches)} branches")
            for branch in branches[:3]:
                print(f"   - {branch['branch_name']}: {branch['total_hours']:.1f} hours, {branch['unique_volunteers']} volunteers")
    
    # 6. Get top volunteers
    print("\n6. Getting top volunteers by hours...")
    response = requests.get(f"{BASE_URL}/volunteers/hours?group_by=volunteer&min_hours=50&start_date=2024-01-01")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            volunteers = data['data']
            print(f"✓ Found {len(volunteers)} volunteers with 50+ hours")
            for vol in volunteers[:5]:
                print(f"   - {vol['name']}: {vol['total_hours']:.1f} hours ({vol['activity_count']} activities)")


def query_specific_branch(branch_code: str = "HQ"):
    """Query statistics for a specific branch"""
    
    print(f"\n7. Getting statistics for branch '{branch_code}'...")
    response = requests.get(f"{BASE_URL}/statistics/branch/{branch_code}?start_date=2024-01-01")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stats = data['data']
            print(f"✓ Branch statistics for {stats['branch_name']}:")
            print(f"   - Total Hours: {stats['total_hours']:.1f}")
            print(f"   - Unique Volunteers: {stats['unique_volunteers']}")
            print(f"   - Average Hours per Volunteer: {stats['average_hours_per_volunteer']:.1f}")
            print(f"   - Total Projects: {stats['unique_projects']}")
            
            if stats['top_volunteers']:
                print("\n   Top volunteers:")
                for name, hours in list(stats['top_volunteers'].items())[:3]:
                    print(f"   - {name}: {hours:.1f} hours")


def export_dashboard_example():
    """Example of exporting an HTML dashboard"""
    
    print("\n8. Exporting HTML dashboard for January 2025...")
    response = requests.get(f"{BASE_URL}/export/dashboard/2025/1")
    
    if response.status_code == 200:
        # Save HTML to file
        with open("dashboard_export.html", "w") as f:
            f.write(response.text)
        print("✓ Dashboard exported to dashboard_export.html")


if __name__ == "__main__":
    print("Starting API client tests...")
    print("Make sure the API server is running: python api_server.py")
    print("")
    
    try:
        test_api()
        query_specific_branch("HQ")
        export_dashboard_example()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Please make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")