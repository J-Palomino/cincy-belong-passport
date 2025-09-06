# YMCA Volunteer Management System

A comprehensive Python application for managing YMCA volunteer data, generating reports, and tracking milestone achievements. Includes both a command-line interface and a REST API for querying volunteer data.

## Features

### 1. Monthly Statistics Dashboard
- Fetch volunteer data from VolunteerMatters API
- Generate comprehensive monthly reports
- Export to JSON, HTML dashboard, and Excel formats
- Track hours by branch, project category, and volunteer

### 2. Milestone Tracking
- Track volunteer service milestones (10, 25, 50, 100, 500 hours)
- Identify volunteers approaching milestones
- Generate recognition lists for awards

### 3. Data Processing
- Automated data deduplication based on YMCA requirements
- Branch credit handling
- Project category analysis
- Member vs non-member volunteer tracking

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Command-Line Interface

#### Test API Connection
```bash
python ymca_volunteer_app.py test
```

### Generate Monthly Report
```bash
# Generate report for January 2025 in all formats
python ymca_volunteer_app.py report --year 2025 --month 1

# Generate only Excel format
python ymca_volunteer_app.py report --year 2025 --month 1 --format excel
```

### Track Milestones
```bash
# Track milestones from January 2024
python ymca_volunteer_app.py milestones --start-date 2024-01-01
```

### Fetch Raw Data
```bash
# Fetch all data from January 2025
python ymca_volunteer_app.py fetch --start-date 2025-01-01

# Fetch data for specific date range
python ymca_volunteer_app.py fetch --start-date 2025-01-01 --end-date 2025-08-31
```

### Option 2: Gradio Web Interface

#### Launch Interactive Web App
```bash
python gradio_app.py
```
This creates an interactive web interface with:
- **Connection Testing** - Verify API connectivity
- **Monthly Reports** - Generate and download reports with visualizations  
- **Milestone Tracking** - Track volunteer achievements and approaching milestones
- **Volunteer Hours Query** - Filter and analyze volunteer data

The app runs on `http://localhost:7860` and provides a **shareable public URL** for easy demonstrations.

### Option 3: REST API Server

#### Start the API Server
```bash
python api_server.py
```
The server will run on `http://localhost:5000`

#### API Endpoints

- `GET /api/health` - Health check
- `GET /api/branches` - Get all branches
- `GET /api/projects/tags` - Get project tags
- `GET /api/report/monthly/{year}/{month}` - Get monthly report
- `GET /api/report/ytd/{year}` - Get year-to-date report
- `GET /api/milestones` - Get milestone achievements
- `GET /api/volunteers/hours` - Get volunteer hours (with filtering)
- `GET /api/statistics/branch/{branch_code}` - Get branch statistics
- `GET /api/export/dashboard/{year}/{month}` - Export HTML dashboard
- `POST /api/cache/clear` - Clear data cache

#### Example API Queries
```bash
# Get January 2025 monthly report summary
curl "http://localhost:5000/api/report/monthly/2025/1?format=summary"

# Get milestone achievements
curl "http://localhost:5000/api/milestones?start_date=2024-01-01"

# Get volunteer hours grouped by branch
curl "http://localhost:5000/api/volunteers/hours?group_by=branch&start_date=2025-01-01"

# Get statistics for a specific branch
curl "http://localhost:5000/api/statistics/branch/HQ?start_date=2024-01-01"
```

#### Test API Client
```bash
python api_client_example.py
```

## Output Files

- **JSON Reports**: `volunteer_report_YYYY_MM.json` - Complete report data
- **HTML Dashboards**: `dashboard_YYYY_MM.html` - Interactive visualizations
- **Excel Reports**: `volunteer_report_YYYY_MM.xlsx` - Formatted spreadsheets
- **Milestone CSVs**: `milestones.csv` and `milestones_approaching.csv`
- **Raw Data**: `raw_volunteer_data.csv` - Cleaned volunteer records

## API Configuration

The application uses hardcoded credentials for the VolunteerMatters API:
- API Key and Secret are embedded in `ymca_volunteer_app.py`
- Customer Code: `cincinnatiymca`

## Data Processing Rules

1. **Zero Hours Removal**: Records with 0 hours are automatically removed
2. **Deduplication**: 
   - Hours: No deduplication (sum all hours)
   - Volunteers: Deduplicated by assignee, project, and branch
   - Projects: Deduplicated by project name and branch
3. **Branch Credit**: Volunteers can be counted at multiple branches

## Milestone Tiers

- 10 Hours: First Impact
- 25 Hours: Service Star
- 50 Hours: Commitment Champion
- 100+ Hours: Passion In Action Award
- 500+ Hours: Guiding Light Award

## Project Structure

- `ymca_volunteer_app.py` - Main CLI application
- `api_server.py` - REST API server
- `volunteer_api_client.py` - VolunteerMatters API client
- `volunteer_data_processor.py` - Data processing and report generation
- `dashboard_generator.py` - Visualization and export functionality
- `api_client_example.py` - Example API client code
- `requirements.txt` - Python dependencies

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test API connection:**
   ```bash
   python ymca_volunteer_app.py test
   ```

3. **Start the API server:**
   ```bash
   python api_server.py
   ```

4. **Generate a monthly report:**
   ```bash
   python ymca_volunteer_app.py report --year 2025 --month 1
   ```

5. **Query the API:**
   ```bash
   python api_client_example.py
   ```

6. **Launch Gradio Web App:**
   ```bash
   python gradio_app.py
   ```
   This creates a shareable web interface at `http://localhost:7860` with a public URL for easy sharing.