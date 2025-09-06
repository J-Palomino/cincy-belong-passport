"""
Gradio Web Application for YMCA Volunteer Management System
Provides a user-friendly interface for generating reports and viewing data
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import io
import base64
from volunteer_api_client import VolunteerMattersAPI
from volunteer_data_processor import VolunteerDataProcessor
from dashboard_generator import DashboardGenerator

# Hardcoded credentials
API_KEY = "62lJN9CLNQbuVag36vFSmDg"
API_SECRET = "oRBbayCJRE2fdJyqKfs9Axw"
CUSTOMER_CODE = "cincinnatiymca"

# Initialize clients
api_client = VolunteerMattersAPI(
    api_key=API_KEY,
    api_secret=API_SECRET,
    customer_code=CUSTOMER_CODE
)
processor = VolunteerDataProcessor(api_client=api_client)
dashboard_gen = DashboardGenerator()

def test_connection():
    """Test API connection"""
    try:
        branches = api_client.get_branches()
        total_branches = branches.get('totalItems', 0)
        
        branch_list = []
        if 'items' in branches and branches['items']:
            for branch in branches['items'][:10]:
                branch_list.append(f"• {branch.get('name')} (Code: {branch.get('code')})")
        
        success_msg = f"✅ **Connection Successful!**\n\n"
        success_msg += f"Found {total_branches} branches:\n\n"
        success_msg += "\n".join(branch_list)
        
        return success_msg
        
    except Exception as e:
        return f"❌ **Connection Failed:**\n\n{str(e)}"

def generate_monthly_report(year, month, format_type):
    """Generate monthly volunteer report"""
    try:
        # Fetch data
        df = processor.fetch_monthly_data(year, month)
        
        if df.empty:
            return "❌ No data found for the specified period", None, None, None
        
        # Generate report
        report = processor.generate_summary_report(
            df,
            month=datetime(year, month, 1).strftime('%B %Y')
        )
        
        # Create summary text
        summary = report['summary']
        month_name = datetime(year, month, 1).strftime('%B %Y')
        
        summary_text = f"# 📊 {month_name} Volunteer Report\n\n"
        summary_text += f"**📈 Key Metrics:**\n"
        summary_text += f"• Total Hours: **{summary['total_hours']:,.0f}**\n"
        summary_text += f"• Active Volunteers: **{summary['total_volunteers']}**\n"
        summary_text += f"• Total Activities: **{summary['total_activities']}**\n"
        summary_text += f"• Unique Projects: **{summary['unique_projects']}**\n"
        summary_text += f"• Branches Involved: **{summary['unique_branches']}**\n\n"
        
        # Add milestone info
        milestones = report['milestones']
        summary_text += f"**🏆 Milestones:**\n"
        summary_text += f"• Volunteers who achieved milestones: **{milestones['total_achieved']}**\n"
        summary_text += f"• Volunteers approaching milestones: **{milestones['total_approaching']}**\n"
        
        # Create visualizations
        branch_hours_fig = dashboard_gen.create_hours_by_branch_chart(report['branch_stats'])
        milestone_fig = dashboard_gen.create_milestone_progress_chart(report['milestones'])
        project_pie_fig = dashboard_gen.create_project_category_pie(report['project_stats'])
        
        # Prepare download file based on format
        download_file = None
        if format_type == "JSON":
            json_str = json.dumps(report, indent=2, default=str)
            download_file = (f"volunteer_report_{year}_{month:02d}.json", json_str)
        elif format_type == "Excel":
            filename = dashboard_gen.export_to_excel(report, f"volunteer_report_{year}_{month:02d}.xlsx")
            download_file = filename
        elif format_type == "HTML":
            html_content = dashboard_gen.create_dashboard_html(report)
            download_file = (f"dashboard_{year}_{month:02d}.html", html_content)
        
        return summary_text, branch_hours_fig, milestone_fig, project_pie_fig, download_file
        
    except Exception as e:
        return f"❌ Error generating report: {str(e)}", None, None, None, None

def track_milestones(start_date, min_hours):
    """Track volunteer milestones"""
    try:
        # Fetch historical data
        history = api_client.get_all_volunteer_history(start_date=start_date)
        df = api_client.volunteer_history_to_dataframe(history)
        
        if df.empty:
            return "❌ No data found for the specified period", None, None
        
        # Remove zero hours
        df = df[df['credited_hours'] > 0]
        
        # Filter by minimum hours if specified
        if min_hours > 0:
            volunteer_totals = df.groupby('contact_id')['credited_hours'].sum()
            qualifying_volunteers = volunteer_totals[volunteer_totals >= min_hours].index
            df = df[df['contact_id'].isin(qualifying_volunteers)]
        
        # Get milestones
        achieved_df = processor.identify_milestone_achievements(df, start_date)
        approaching_df = processor.get_volunteers_approaching_milestones(df)
        
        # Create summary
        summary_text = f"# 🏆 Milestone Tracking Report\n\n"
        summary_text += f"**📅 Tracking Period:** From {start_date}\n"
        summary_text += f"**📊 Data Summary:**\n"
        summary_text += f"• Total Records: **{len(df)}**\n"
        summary_text += f"• Unique Volunteers: **{df['contact_id'].nunique()}**\n"
        summary_text += f"• Total Hours Tracked: **{df['credited_hours'].sum():,.0f}**\n\n"
        
        summary_text += f"**🎯 Milestone Achievements:**\n"
        summary_text += f"• Volunteers who achieved milestones: **{len(achieved_df)}**\n"
        summary_text += f"• Volunteers approaching milestones: **{len(approaching_df)}**\n\n"
        
        if not achieved_df.empty:
            summary_text += "**🏅 Recent Achievements:**\n"
            for _, volunteer in achieved_df.head(10).iterrows():
                summary_text += f"• **{volunteer['name']}**: {volunteer['award_name']} ({volunteer['total_hours']:.0f} hours)\n"
        
        # Create milestone chart
        milestone_fig = dashboard_gen.create_milestone_progress_chart({'achieved': achieved_df.to_dict('records')})
        
        # Create approaching milestones table
        approaching_table = None
        if not approaching_df.empty:
            approaching_table = approaching_df[['name', 'current_hours', 'next_milestone', 'hours_needed', 'next_award']].head(20)
        
        return summary_text, milestone_fig, approaching_table
        
    except Exception as e:
        return f"❌ Error tracking milestones: {str(e)}", None, None

def get_volunteer_hours(start_date, end_date, branch_filter, group_by, min_hours):
    """Get volunteer hours with filters"""
    try:
        # Fetch data
        history = api_client.get_all_volunteer_history(
            start_date=start_date,
            end_date=end_date
        )
        df = api_client.volunteer_history_to_dataframe(history)
        
        if df.empty:
            return "❌ No data found for the specified period", None
        
        # Remove zero hours
        df = df[df['credited_hours'] > 0]
        
        # Apply branch filter
        if branch_filter and branch_filter != "All":
            df = df[df['branch_code'] == branch_filter]
        
        # Group data
        if group_by == "Volunteer":
            result = df.groupby(['contact_id', 'full_name', 'contact_email']).agg({
                'credited_hours': 'sum',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['Contact ID', 'Name', 'Email', 'Total Hours', 'Activities']
        
        elif group_by == "Branch":
            result = df.groupby(['branch_name', 'branch_code']).agg({
                'credited_hours': 'sum',
                'contact_id': 'nunique',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['Branch Name', 'Branch Code', 'Total Hours', 'Unique Volunteers', 'Activities']
        
        elif group_by == "Project":
            result = df.groupby(['project_name']).agg({
                'credited_hours': 'sum',
                'contact_id': 'nunique',
                'volunteer_date': 'count'
            }).reset_index()
            result.columns = ['Project Name', 'Total Hours', 'Unique Volunteers', 'Activities']
        
        # Apply minimum hours filter
        if min_hours > 0 and 'Total Hours' in result.columns:
            result = result[result['Total Hours'] >= min_hours]
        
        # Sort by total hours
        if 'Total Hours' in result.columns:
            result = result.sort_values('Total Hours', ascending=False)
        
        # Create summary
        summary_text = f"# 📊 Volunteer Hours Report\n\n"
        summary_text += f"**📅 Period:** {start_date} to {end_date or 'present'}\n"
        summary_text += f"**🏢 Branch Filter:** {branch_filter or 'All'}\n"
        summary_text += f"**👥 Grouped By:** {group_by}\n"
        summary_text += f"**⏰ Min Hours:** {min_hours}\n\n"
        summary_text += f"**📈 Results:** {len(result)} records found\n"
        if 'Total Hours' in result.columns:
            summary_text += f"**⏱️ Total Hours:** {result['Total Hours'].sum():,.0f}\n"
        
        return summary_text, result
        
    except Exception as e:
        return f"❌ Error getting volunteer hours: {str(e)}", None

def get_branch_list():
    """Get list of available branches"""
    try:
        branches = api_client.get_branches()
        branch_options = ["All"]
        if 'items' in branches:
            for branch in branches['items']:
                branch_options.append(branch.get('code', ''))
        return branch_options
    except:
        return ["All", "HQ", "Downtown_East"]

# Create Gradio interface
def create_interface():
    # Custom CSS for better styling
    css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .gr-button-primary {
        background: linear-gradient(45deg, #003f7f, #0095da) !important;
        border: none !important;
    }
    """
    
    with gr.Blocks(css=css, title="YMCA Volunteer Management System", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🏢 YMCA of Greater Cincinnati - Volunteer Management System
        
        **Comprehensive tool for analyzing volunteer data, tracking milestones, and generating reports**
        """)
        
        with gr.Tabs():
            # Connection Test Tab
            with gr.Tab("🔗 Connection Test"):
                gr.Markdown("### Test VolunteerMatters API Connection")
                
                test_btn = gr.Button("Test Connection", variant="primary", size="lg")
                connection_output = gr.Markdown()
                
                test_btn.click(
                    fn=test_connection,
                    outputs=connection_output
                )
            
            # Monthly Reports Tab
            with gr.Tab("📊 Monthly Reports"):
                gr.Markdown("### Generate Monthly Volunteer Reports")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        report_year = gr.Number(
                            label="Year", 
                            value=2025, 
                            precision=0,
                            minimum=2020,
                            maximum=2030
                        )
                        report_month = gr.Slider(
                            label="Month", 
                            minimum=1, 
                            maximum=12, 
                            value=1, 
                            step=1
                        )
                        report_format = gr.Dropdown(
                            label="Export Format",
                            choices=["JSON", "Excel", "HTML"],
                            value="JSON"
                        )
                        generate_btn = gr.Button("Generate Report", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        report_summary = gr.Markdown()
                
                with gr.Row():
                    branch_hours_plot = gr.Plot(label="Hours by Branch")
                    milestone_plot = gr.Plot(label="Milestone Achievements")
                
                project_pie_plot = gr.Plot(label="Hours by Project Category")
                
                download_file = gr.File(label="Download Report")
                
                generate_btn.click(
                    fn=generate_monthly_report,
                    inputs=[report_year, report_month, report_format],
                    outputs=[report_summary, branch_hours_plot, milestone_plot, project_pie_plot, download_file]
                )
            
            # Milestone Tracking Tab
            with gr.Tab("🏆 Milestone Tracking"):
                gr.Markdown("### Track Volunteer Milestone Achievements")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        milestone_start_date = gr.Textbox(
                            label="Start Date (YYYY-MM-DD)", 
                            value="2024-01-01"
                        )
                        milestone_min_hours = gr.Number(
                            label="Minimum Hours (0 for all)", 
                            value=0,
                            minimum=0
                        )
                        track_btn = gr.Button("Track Milestones", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        milestone_summary = gr.Markdown()
                
                with gr.Row():
                    milestone_chart = gr.Plot(label="Milestone Achievements")
                    approaching_table = gr.Dataframe(label="Volunteers Approaching Milestones")
                
                track_btn.click(
                    fn=track_milestones,
                    inputs=[milestone_start_date, milestone_min_hours],
                    outputs=[milestone_summary, milestone_chart, approaching_table]
                )
            
            # Volunteer Hours Tab
            with gr.Tab("⏱️ Volunteer Hours"):
                gr.Markdown("### Query Volunteer Hours with Filters")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        hours_start_date = gr.Textbox(
                            label="Start Date (YYYY-MM-DD)", 
                            value="2025-01-01"
                        )
                        hours_end_date = gr.Textbox(
                            label="End Date (YYYY-MM-DD, optional)", 
                            value=""
                        )
                        hours_branch = gr.Dropdown(
                            label="Branch Filter",
                            choices=get_branch_list(),
                            value="All"
                        )
                        hours_group_by = gr.Dropdown(
                            label="Group By",
                            choices=["Volunteer", "Branch", "Project"],
                            value="Volunteer"
                        )
                        hours_min_hours = gr.Number(
                            label="Minimum Hours", 
                            value=0,
                            minimum=0
                        )
                        query_btn = gr.Button("Query Hours", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        hours_summary = gr.Markdown()
                
                hours_table = gr.Dataframe(label="Results", height=400)
                
                query_btn.click(
                    fn=get_volunteer_hours,
                    inputs=[hours_start_date, hours_end_date, hours_branch, hours_group_by, hours_min_hours],
                    outputs=[hours_summary, hours_table]
                )
        
        # Footer
        gr.Markdown("""
        ---
        **🏢 YMCA of Greater Cincinnati Volunteer Management System**  
        *Built with Python, Gradio, and the VolunteerMatters API*
        """)
    
    return app

if __name__ == "__main__":
    print("Starting YMCA Volunteer Management Gradio App...")
    
    # Create and launch the app
    app = create_interface()
    
    # Launch with sharing enabled
    app.launch(
        share=True,  # This creates a public shareable link
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        favicon_path=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        ssl_keyfile_password=None,
        debug=False
    )