"""
REST API Server for YMCA Volunteer Data
Provides endpoints to query volunteer reports and data
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from volunteer_api_client import VolunteerMattersAPI
from volunteer_data_processor import VolunteerDataProcessor
from dashboard_generator import DashboardGenerator
import threading
import time
from functools import lru_cache

# Hardcoded credentials
API_KEY = "62lJN9CLNQbuVag36vFSmDg"
API_SECRET = "oRBbayCJRE2fdJyqKfs9Axw"
CUSTOMER_CODE = "cincinnatiymca"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache for storing fetched data
data_cache = {}
cache_lock = threading.Lock()

# Initialize API client and processor
api_client = VolunteerMattersAPI(
    api_key=API_KEY,
    api_secret=API_SECRET,
    customer_code=CUSTOMER_CODE
)
processor = VolunteerDataProcessor(api_client=api_client)


def get_cache_key(year: int, month: int = None):
    """Generate cache key for data"""
    if month:
        return f"{year}_{month:02d}"
    return f"{year}_full"


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'YMCA Volunteer API'
    })


@app.route('/api/branches', methods=['GET'])
def get_branches():
    """Get all branches"""
    try:
        branches = api_client.get_branches()
        return jsonify({
            'success': True,
            'data': branches
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/tags', methods=['GET'])
def get_project_tags():
    """Get all project tags"""
    try:
        tags = api_client.get_project_tags()
        return jsonify({
            'success': True,
            'data': tags
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/monthly/<int:year>/<int:month>', methods=['GET'])
def get_monthly_report(year: int, month: int):
    """
    Get monthly volunteer report
    
    Query params:
    - format: json (default), summary, or full
    - refresh: true to force refresh cache
    """
    try:
        format_type = request.args.get('format', 'json')
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        cache_key = get_cache_key(year, month)
        
        # Check cache unless refresh requested
        if not refresh and cache_key in data_cache:
            report = data_cache[cache_key]
        else:
            # Fetch fresh data
            df = processor.fetch_monthly_data(year, month)
            
            if df.empty:
                return jsonify({
                    'success': False,
                    'error': 'No data found for specified period'
                }), 404
            
            # Generate report
            report = processor.generate_summary_report(
                df,
                month=datetime(year, month, 1).strftime('%B %Y')
            )
            
            # Cache the report
            with cache_lock:
                data_cache[cache_key] = report
        
        # Return based on format
        if format_type == 'summary':
            return jsonify({
                'success': True,
                'data': report['summary']
            })
        elif format_type == 'full':
            return jsonify({
                'success': True,
                'data': report
            })
        else:
            return jsonify({
                'success': True,
                'data': report
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/ytd/<int:year>', methods=['GET'])
def get_ytd_report(year: int):
    """
    Get year-to-date volunteer report
    
    Query params:
    - up_to_month: Month to include up to (default: current month)
    """
    try:
        up_to_month = request.args.get('up_to_month', type=int)
        
        # Fetch YTD data
        df = processor.fetch_ytd_data(year, up_to_month)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found for specified period'
            }), 404
        
        # Generate report
        report = processor.generate_summary_report(
            df,
            month=f"YTD {year}"
        )
        
        return jsonify({
            'success': True,
            'data': report
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/milestones', methods=['GET'])
def get_milestones():
    """
    Get milestone achievements and approaching volunteers
    
    Query params:
    - start_date: Start date for calculation (default: 2024-01-01)
    - threshold_percent: Percentage to consider "approaching" (default: 0.8)
    """
    try:
        start_date = request.args.get('start_date', '2024-01-01')
        threshold_percent = request.args.get('threshold_percent', 0.8, type=float)
        
        # Fetch historical data
        history = api_client.get_all_volunteer_history(start_date=start_date)
        df = api_client.volunteer_history_to_dataframe(history)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found'
            }), 404
        
        # Remove zero hours
        df = df[df['credited_hours'] > 0]
        
        # Get milestones
        achieved_df = processor.identify_milestone_achievements(df, start_date)
        approaching_df = processor.get_volunteers_approaching_milestones(df, threshold_percent)
        
        response = {
            'success': True,
            'data': {
                'achieved': achieved_df.to_dict('records') if not achieved_df.empty else [],
                'approaching': approaching_df.to_dict('records') if not approaching_df.empty else [],
                'summary': {
                    'total_achieved': len(achieved_df),
                    'total_approaching': len(approaching_df),
                    'calculation_start_date': start_date
                }
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/volunteers/hours', methods=['GET'])
def get_volunteer_hours():
    """
    Get volunteer hours by various filters
    
    Query params:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - branch_code: Filter by branch
    - min_hours: Minimum hours threshold
    - group_by: Group results by (volunteer, branch, project)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        branch_code = request.args.get('branch_code')
        min_hours = request.args.get('min_hours', 0, type=float)
        group_by = request.args.get('group_by', 'volunteer')
        
        # Fetch data
        history = api_client.get_all_volunteer_history(
            start_date=start_date,
            end_date=end_date
        )
        df = api_client.volunteer_history_to_dataframe(history)
        
        if df.empty:
            return jsonify({
                'success': True,
                'data': []
            })
        
        # Remove zero hours
        df = df[df['credited_hours'] > 0]
        
        # Apply branch filter if provided
        if branch_code:
            df = df[df['branch_code'] == branch_code]
        
        # Group data based on parameter
        if group_by == 'volunteer':
            result = df.groupby(['contact_id', 'full_name', 'contact_email']).agg({
                'credited_hours': 'sum',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['contact_id', 'name', 'email', 'total_hours', 'activity_count']
        
        elif group_by == 'branch':
            result = df.groupby(['branch_name', 'branch_code']).agg({
                'credited_hours': 'sum',
                'contact_id': 'nunique',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['branch_name', 'branch_code', 'total_hours', 'unique_volunteers', 'activity_count']
        
        elif group_by == 'project':
            result = df.groupby(['project_name', 'project_id']).agg({
                'credited_hours': 'sum',
                'contact_id': 'nunique',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['project_name', 'project_id', 'total_hours', 'unique_volunteers', 'activity_count']
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid group_by parameter. Use: volunteer, branch, or project'
            }), 400
        
        # Apply minimum hours filter
        if min_hours > 0:
            result = result[result['total_hours'] >= min_hours]
        
        # Sort by total hours descending
        result = result.sort_values('total_hours', ascending=False)
        
        return jsonify({
            'success': True,
            'data': result.to_dict('records'),
            'summary': {
                'total_records': len(result),
                'total_hours': result['total_hours'].sum() if 'total_hours' in result.columns else 0,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics/branch/<branch_code>', methods=['GET'])
def get_branch_statistics(branch_code: str):
    """
    Get detailed statistics for a specific branch
    
    Query params:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Fetch data
        history = api_client.get_all_volunteer_history(
            start_date=start_date,
            end_date=end_date
        )
        df = api_client.volunteer_history_to_dataframe(history)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found'
            }), 404
        
        # Filter by branch
        df = df[df['branch_code'] == branch_code]
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for branch {branch_code}'
            }), 404
        
        # Calculate statistics
        stats = {
            'branch_code': branch_code,
            'branch_name': df['branch_name'].iloc[0] if 'branch_name' in df.columns else branch_code,
            'total_hours': df['credited_hours'].sum(),
            'unique_volunteers': df['contact_id'].nunique(),
            'total_activities': len(df),
            'unique_projects': df['project_name'].nunique(),
            'average_hours_per_volunteer': df['credited_hours'].sum() / df['contact_id'].nunique(),
            'date_range': {
                'start': df['volunteer_date'].min().isoformat() if not df.empty else None,
                'end': df['volunteer_date'].max().isoformat() if not df.empty else None
            },
            'top_volunteers': df.groupby(['full_name', 'contact_email'])['credited_hours'].sum().nlargest(10).to_dict(),
            'projects': df.groupby('project_name')['credited_hours'].sum().to_dict()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/dashboard/<int:year>/<int:month>', methods=['GET'])
def export_dashboard(year: int, month: int):
    """Generate and return HTML dashboard"""
    try:
        # Get or generate report
        cache_key = get_cache_key(year, month)
        
        if cache_key in data_cache:
            report = data_cache[cache_key]
        else:
            df = processor.fetch_monthly_data(year, month)
            
            if df.empty:
                return jsonify({
                    'success': False,
                    'error': 'No data found for specified period'
                }), 404
            
            report = processor.generate_summary_report(
                df,
                month=datetime(year, month, 1).strftime('%B %Y')
            )
            
            with cache_lock:
                data_cache[cache_key] = report
        
        # Generate HTML
        generator = DashboardGenerator()
        html_content = generator.create_dashboard_html(report)
        
        # Return HTML as response
        return html_content, 200, {'Content-Type': 'text/html'}
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the data cache"""
    try:
        with cache_lock:
            data_cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("Starting YMCA Volunteer API Server...")
    print("API Documentation:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/branches - Get all branches")
    print("  GET  /api/projects/tags - Get project tags")
    print("  GET  /api/report/monthly/<year>/<month> - Get monthly report")
    print("  GET  /api/report/ytd/<year> - Get year-to-date report")
    print("  GET  /api/milestones - Get milestone achievements")
    print("  GET  /api/volunteers/hours - Get volunteer hours")
    print("  GET  /api/statistics/branch/<branch_code> - Get branch statistics")
    print("  GET  /api/export/dashboard/<year>/<month> - Export HTML dashboard")
    print("  POST /api/cache/clear - Clear data cache")
    print("\nServer running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)