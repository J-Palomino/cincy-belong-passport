Wishlist #1: YMCA Monthly Volunteer Statistics Report Dashboard
Purpose:
To provide a clear, accurate snapshot of monthly volunteer engagement across the YMCA
association—hours served, active volunteers, member involvement, and project types—using data
from VolunteerMatters and internal tools.

�� Tools &amp; Resources Used:
1. VolunteerMatters: Volunteer History Report (Excel export)
2. Power Point File:
o Y Volunteer Monthly Statistical Report (7.31.2025 &amp; 8.31.2025)
3. Excel Files:
o Y Volunteer 2025 Statistic Worksheet
o Raw Volunteer Data – Jan–Aug 2025 &amp; Jan – July 2025
4. API:
VolunteerMatters API Swagger UI

�� Step 1: Data Extraction
● Download the Volunteer History Report from VolunteerMatters.
o Date filters:
▪ Start: January 1, 2025
▪ End: First day of the month being reported
o This ensures that only completed volunteer activities are included.

�� Step 2: Prepare the Data
● Delete all rows where Hours = 0
Volunteers with 0 hours only registered but did not complete the activity.
Save as &quot;Raw Data&quot; file to use for multiple deduplication/pivot steps.
�� Notes:
● Deduplication is key: Numbers vary depending on whether you’re counting by activity,
person, or location. Each data set requires its own logic.
● Branch Credit: Volunteers may be counted at more than one branch, and branches get credit
for both volunteer time and member participation.

● Manual Adjustments: Some branches or programs (like swim) require tailored adjustments to
reflect true engagement. I also need to check data monthly for reporting errors prior to pulling
data.

�� Step 3: Page 1: Project Category Statistics - I create the data in Raw Volunteer Data –
Jan–Aug 2025, then put it in the Y Volunteer 2025 Statistic Worksheet to use in the Powerpoint: Y
Monthly Statistics Report 8.31.2025
1. Hours (no deduplication)
o Use a pivot table: PROJECT TAG and HOURS (sum)
2. Volunteers
o Deduplicate by: ASSIGNEE, PROJECT CATALOG, BRANCH
o Use a pivot table: PROJECT CATALOG AND ASSIGNEE(count).
o Reason: Volunteers may serve in multiple branches or in multiple categories.
3. Projects
o Deduplicate by: PROJECT, PROJECT CATALOG, BRANCH
o Manually adjust numbers for Competitive Swim and Gymnastics (which often split
projects for accounting). We have 6 projects total.
o Use pivot: PROJECT TAG vs PROJECT (count)

Pages 2–5: Branch/Site Breakdown: I create the data in Raw Volunteer Data – Jan–Aug 2025,
then put it in the Y Volunteer 2025 Statistic Worksheet to use in the Powerpoint: Y Monthly Statistics
Report 8.31.2025.

1. Branch – Hours: Total Hours (no deduplication)
o Use BRANCH and HOURS sum) in a pivot table
2. Active Volunteers
o Deduplicate by: ASSIGNEE, BRANCH
o Use BRANCH and Assignee (county) in a pivot table
3. Member Volunteers
o Use the data that was depulicated for Active Volunteers to determine the member
information:
o Use MEMBER BRANCH and ARE YOU A YMCA MEMBER in a pivot table,

o Filter by &quot;Yes&quot;
o Pivot to count by MEMBER BRANCH

Special Reports:
Page 6 – The Youth Development and Education department is broken down by Project
Tag (YDE – Community Services, YDE – Early Learning Centers, and YDE - Out of School
Time) to determine their Hours, Volunteers, and Project numbers using the filtering of the pivot
tables. Music Resource Center which is listed as a site is also added to the YDE- Community
Services section fo this report.

Page 7 – YMCA &amp; Senior Centers – Two YMCAs have Senior Centers and this page
combines the information from the Y Volunteer 2025 Statistic Worksheets for ease of reading.

● Clippard YMCA + Clippard Senior Center
● R.C. Durre YMCA + Kentucky Senior Center

Wishlist #2: Volunteer Hours Milestone Tracker &amp; Aids to Recognize
Service
Design a simple, replicable tool that pulls volunteer hour data from VolunteerMatters reports to
automatically identify and flag service hour milestones — enabling the YMCA to recognize
volunteers in real time across all branches.

Why This Matters:
Tracking and celebrating volunteer contributions as they happen reinforces a culture of recognition,
belonging, and purpose. Right now, volunteer hours are logged, but milestones (10, 25, 50, 100+
hours) are recognized only annually.

What We’re Asking You to Do:
Deliverable:
A working prototype or framework (manual or automated) that:
● Pulls data from VolunteerMatters (via API pull or VolunteerMatters – VolunteerHistory report),
Starting with January 1, 2024.
● Flags milestone achievements for volunteers
● Outputs notifications, report views, or recognition triggers
Optional Add-ons (if time permits):
● Email or badge template for milestone recognition (Daxko Engage)
● Dashboard view - Google Doc, Excel, Power BI, etc
● Documentation for staff to maintain and replicate the process

Resources Provided:
● Sample VolunteerMatters report export Excel File: Raw Volunteer Data – Jan–Aug 2025 &amp;
Jan – July 2025
● API:
VolunteerMatters API Swagger UI
● Milestone definitions
● Recognition templates (badge names, email messages)
● Staff contacts for testing or validation

Milestone Tiers:
● 10 Hours → “First Impact” - New
● 25 Hours → “Service Star” - New
● 50 Hours → “Commitment Champion” - New
● 100+ Hours → “Passion In Action Award ” – Received t-shirt
● 500+ Hours → “Guiding Light Award” – Received glass engraved star

Success Looks Like:
By the end of the day, we’ll have:
● A prototype or working model that can track milestones
● Clear handoff documentation
● Enthusiastic buy-in from staff who are ready to implement it

Wishlist #3 &amp; #4: Volunteer PathFinder: AI Agent for Matching Passion
with Purpose
Design a user-friendly AI assistant prototype that supports individuals in exploring, understanding,
and navigating YMCA volunteer opportunities — helping them find a role that aligns with their
interests, availability, and skills.
Why This Matters:
People want to contribute, but many face barriers in understanding where they fit within the YMCA.
The current process involves multiple platforms (VolunteerMatters, myy.org, guides, training and
human conversation), and volunteers often need help connecting the dots.
Your task is to simplify that journey through an AI tool that’s helpful, clear, and welcoming.

Main Deliverable:
A working AI assistant prototype or scripted experience that can:
● Respond to questions about volunteering (e.g. requirements, process, types of opportunities)
● Guide a user step-by-step through onboarding via VolunteerMatters
● Recommend opportunities based on user input (interests, age, schedule)
● Point to relevant pages or resources from myy.org, VolunteerMatters Project Catalog, YMCA
Volunteer handbook
● Optional Add-ons (if time allows):
● Simulate chat-style experience using a no-code chatbot builder or script
● Draft sample Q&amp;A responses based on frequently asked questions
● Include links or embed visuals that guide users to the next step

Resources Available:
● YMCA of Greater Cincinnati’s Volunteer Page: https://www.myy.org/volunteering -
● Contains:
o Link to the VolunteerMatters Project Catalog that lists all volunteer projects made
public for consideration: https://cincinnatiymca.volunteermatters.org/project-catalog
o Link to a Interest form already in use that once completed is sent to the Executive
Director via email per branch:
https://ymcacincinnati.qualtrics.com/jfe/form/SV_0JklTjQEJTQmS2i
o On website, there is answers to Frequently Asked Questions about volunteering and
locations of each branch/site.

● Excel Document:
o YMCA Volunteer Project Description Sheet - Contains names of Projects, Branch
locations, Description of activities which includes dates, type of project, contact
information
o YMCA of Greater Cincinnati Handbook
o Volunteer Screening Matrix- a chart on credentials and forms needed to be completed
in order to volunteer.
o Application for One Day Event Child Protection Policy *This is only used when someone
cannot utilize the VolunteerMatters platform.
5. VolunteerMatters API: VolunteerMatters API Swagger UI
● Sample VolunteerMatters registration flow: Direct Link to create an account on
VolulnteeMatter: https://cincinnatiymca.volunteermatters.org/volunteer/register
● Staff available for real-time questions/validation

Success by End of Day Means:
● A functioning or clearly designed assistant that supports new volunteers through the
recruitment process
● A tool or script that feels friendly, accurate, and aligned with YMCA expectations
● Clear documentation of how it works and how staff or branches might use it

Purpose &amp; Impact:
This project will help individuals explore volunteering with confidence and clarity — making it easier to
take the first step and contribute in a way that’s meaningful to them and aligned with YMCA needs.
Thank you for using your time and skills to strengthen the volunteer experience at the YMCA.
