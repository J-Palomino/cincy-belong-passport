# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the Future of Data project focused on developing volunteer management solutions for the YMCA of Greater Cincinnati. The project aims to create data dashboards, tracking systems, and AI assistants to improve volunteer engagement and recognition.

## Key Project Components

### Wishlist #1: Monthly Volunteer Statistics Report Dashboard
- Creates monthly reports from VolunteerMatters data exports
- Tracks volunteer hours, active volunteers, member involvement, and project types
- Requires data deduplication and pivot table manipulation
- Outputs to PowerPoint presentations and Excel worksheets

### Wishlist #2: Volunteer Hours Milestone Tracker
- Tracks volunteer service milestones (10, 25, 50, 100+ hours)
- Pulls data from VolunteerMatters API or history reports
- Identifies volunteers for recognition at milestone achievements
- Milestone tiers: First Impact (10h), Service Star (25h), Commitment Champion (50h), Passion In Action Award (100h+), Guiding Light Award (500h+)

### Wishlist #3 & 4: Volunteer PathFinder AI Assistant
- AI-powered assistant to help match volunteers with opportunities
- Guides users through VolunteerMatters onboarding
- Recommends opportunities based on interests, skills, and availability
- Integrates with existing YMCA resources and platforms

## Data Sources and APIs

### VolunteerMatters
- Primary data source for volunteer information
- API available via Swagger UI
- Volunteer History Report exports (Excel format)
- Project Catalog: https://cincinnatiymca.volunteermatters.org/project-catalog
- Registration URL: https://cincinnatiymca.volunteermatters.org/volunteer/register

### Key Data Files
- Y Volunteer 2025 Statistic Worksheet
- Raw Volunteer Data files (monthly exports)
- YMCA Volunteer Project Description Sheet
- Volunteer Screening Matrix

## Data Processing Requirements

### Critical Data Operations
- **Deduplication Logic**: Different counts required for activities, persons, and locations
- **Branch Credit**: Volunteers may be counted at multiple branches
- **Manual Adjustments**: Some programs (swim, gymnastics) require special handling
- **Data Filtering**: Remove rows where Hours = 0 (registered but incomplete activities)

### Pivot Table Configurations
- Hours by Project Tag (no deduplication)
- Volunteers by Assignee/Project/Branch (deduplicated)
- Member volunteers filtered by "Yes" response
- Branch statistics combining YMCA and Senior Centers

## External Resources

- YMCA Volunteering Page: https://www.myy.org/volunteering
- Interest Form: https://ymcacincinnati.qualtrics.com/jfe/form/SV_0JklTjQEJTQmS2i
- YMCA of Greater Cincinnati Handbook
- Volunteer Screening Matrix documentation

## Development Guidelines

When working on this project:
- Preserve exact data processing logic from existing workflows
- Maintain compatibility with VolunteerMatters data exports
- Consider branch-specific requirements and exceptions
- Focus on automation while allowing for manual adjustments where needed
- Ensure recognition systems align with established milestone tiers