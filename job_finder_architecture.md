# Automatic Job Finder — System Architecture

## 1. Project Overview

An automated job-finding and application-management platform where each user can:

- Create an account / log in with Google.
- Maintain a personal application profile.
- Upload and manage resumes, marksheets, certificates, and other documents.
- Define job preferences.
- Automatically discover relevant jobs from supported job sources.
- Receive ranked/matched job recommendations.
- Track applications and their status.
- View application history.
- Optionally connect Gmail to detect application-related emails.
- Open job application links or use assisted/automated application workflows where supported.

---

## 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FRONTEND        │
                         │   React / Next.js    │
                         └──────────┬───────────┘
                                    │
                              REST / API
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       BACKEND        │
                         │     FastAPI/Python   │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │    SUPABASE   │     │  JOB SOURCES  │     │   GMAIL API   │
      │               │     │               │     │               │
      │ Auth          │     │ APIs / Feeds  │     │ Application   │
      │ PostgreSQL    │     │ Permitted     │     │ Emails        │
      │ Storage       │     │ Sources       │     │               │
      └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
              │                     │                     │
              │                     ▼                     │
              │            ┌────────────────┐             │
              │            │   JOB ENGINE    │◄────────────┘
              │            │                 │
              │            │ Search          │
              │            │ Normalize       │
              │            │ Deduplicate     │
              │            │ Filter          │
              │            │ Match / Rank    │
              │            └───────┬────────┘
              │                    │
              └────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │      DASHBOARD       │
                         │ Jobs / Applications  │
                         │ History / Alerts     │
                         └──────────────────────┘
```

---

## 3. Technology Stack

### Frontend
- React or Next.js
- HTML/CSS/JavaScript
- Tailwind CSS (optional)

### Backend
- Python
- FastAPI
- REST API

### Database / Backend Services
- Supabase
  - PostgreSQL database
  - Authentication
  - Storage
  - Row Level Security (RLS)

### External Services
- Google OAuth
- Gmail API (optional)
- Job APIs / permitted job feeds / permitted web sources

### Matching
Start simple:
- Keyword matching
- Skill matching
- Weighted scoring

Later:
- TF-IDF + cosine similarity
- Embeddings
- LLM-based semantic matching

---

# 4. Main Modules

## 4.1 Authentication Module

Purpose:
- Register/login users.
- Support Google login.
- Maintain authenticated sessions.

Flow:

```text
User
  │
  ▼
Google Login / Email Login
  │
  ▼
Supabase Auth
  │
  ▼
Authenticated User
  │
  ▼
User ID used throughout application
```

Important:
- Every user-owned database record must contain a `user_id`.
- Supabase Row Level Security should prevent users from accessing another user's data.

---

# 5. User Profile Module

The user enters information once and reuses it for applications.

### Personal Information

- Full name
- Email
- Phone
- Location
- Address
- LinkedIn
- GitHub
- Portfolio

### Education

- Institution
- Degree
- Branch
- CGPA
- Graduation year
- 10th marks
- 12th marks

### Experience

- Company
- Position
- Duration
- Description

### Skills

- Programming languages
- Frameworks
- Databases
- Cloud technologies
- Tools
- Other skills

---

# 6. Document Management

Documents should be stored in **Supabase Storage**, not directly inside PostgreSQL.

Possible documents:

```text
Resume
Cover Letter
10th Marksheet
12th Marksheet
College Marksheet
Certificates
Other Documents
```

Architecture:

```text
User
 │
 ▼
Frontend Upload
 │
 ▼
Supabase Storage
 │
 ├── resumes/
 ├── marksheets/
 ├── certificates/
 └── other/
```

The database stores metadata such as:

```text
document_id
user_id
document_type
file_name
storage_path
created_at
```

---

# 7. Job Preferences Module

Users define what jobs they want.

Example:

```text
Job Titles:
- Software Engineer
- Backend Developer

Locations:
- Chennai
- Bangalore
- Hyderabad

Skills:
- Python
- Java
- SQL

Experience:
- 0–2 years

Minimum Salary:
- ₹6 LPA

Job Type:
- Full-time

Remote:
- Preferred
```

These preferences are used by the Job Engine.

---

# 8. Job Search Engine

The Job Engine is responsible for discovering jobs.

```text
User Preferences
       │
       ▼
Search Jobs
       │
       ├── Source 1
       ├── Source 2
       └── Source 3
       │
       ▼
Normalize Data
       │
       ▼
Remove Duplicates
       │
       ▼
Filter
       │
       ▼
Match / Rank
       │
       ▼
Save Relevant Jobs
       │
       ▼
Notify User
```

Use job sources that provide APIs, feeds, or otherwise permit automated access.

Avoid designing the system around defeating CAPTCHA, anti-bot systems, rate limits, or access controls.

---

# 9. Job Data Model

All sources should be converted into one common format.

Example:

```json
{
  "title": "Software Engineer",
  "company": "Example Company",
  "location": "Chennai",
  "description": "...",
  "salary": "₹8-12 LPA",
  "url": "...",
  "source": "Example Source",
  "posted_at": "2026-09-08"
}
```

This allows the frontend to display jobs consistently regardless of their source.

---

# 10. Job Matching and Ranking

## Version 1 — Rule-Based Matching

Recommended for the first implementation.

Example weighting:

```text
Skill Match       40%
Job Title Match   25%
Location Match    15%
Experience Match  10%
Salary Match      10%
```

Example:

```text
Backend Developer
Match: 92%

Python        ✓
FastAPI       ✓
PostgreSQL    ✓
Chennai       ✓
0–2 years     ✓
```

The final score can be stored with the job-user recommendation.

## Future Version — AI Matching

Possible upgrades:

```text
Resume
   +
Job Description
   │
   ▼
Text Processing
   │
   ▼
Embeddings
   │
   ▼
Similarity Score
   │
   ▼
AI Match Explanation
```

Example:

> 92% match because the role requires Python, SQL, backend development, and 0–2 years of experience.

---

# 11. Application Management

Every time a user decides to apply, create an application record.

Possible statuses:

```text
FOUND
SAVED
APPLIED
UNDER_REVIEW
INTERVIEW
ACCEPTED
REJECTED
WITHDRAWN
```

Application flow:

```text
Job Found
   │
   ▼
User Saves Job
   │
   ▼
User Applies
   │
   ▼
Application Created
   │
   ▼
Status = APPLIED
   │
   ├── UNDER_REVIEW
   ├── INTERVIEW
   ├── ACCEPTED
   └── REJECTED
```

---

# 12. Gmail Integration

Gmail integration is optional and should be implemented after the core job system works.

Purpose:

- Detect application confirmation emails.
- Detect rejection emails.
- Detect interview invitations.
- Detect offer emails.
- Update application status.

Flow:

```text
Gmail
  │
  ▼
Gmail API
  │
  ▼
Backend
  │
  ▼
Identify Job Application Email
  │
  ▼
Extract Company / Job
  │
  ▼
Classify Email
  │
  ▼
Update Application
```

Example:

```text
"Thank you for applying..."
        ↓
APPLIED / UNDER_REVIEW

"We have decided not to move forward..."
        ↓
REJECTED

"We would like to invite you..."
        ↓
INTERVIEW
```

Gmail access must be explicitly authorized by the user.

---

# 13. Application Workflow

## Recommended V1: Assisted Application

Instead of fully automatic submission, the first version should prepare the application and let the user review it.

```text
Job Found
   │
   ▼
Match Score > Threshold
   │
   ▼
Prepare Application
   │
   ├── Personal Information
   ├── Resume
   ├── Education
   └── Other Documents
   │
   ▼
Open Application Link
   │
   ▼
User Reviews
   │
   ▼
User Submits
```

This is much easier and more reliable than trying to automatically submit every type of application form.

---

# 14. Future Automatic Application Module

A later version could support automated form filling where the target application workflow permits it.

```text
Job Found
   │
   ▼
High Match
   │
   ▼
Application Preparation
   │
   ▼
Form Filling
   │
   ▼
Document Upload
   │
   ▼
User Review
   │
   ▼
Submit
```

Do not build the system around bypassing CAPTCHA, bot detection, authentication barriers, or other access controls.

---

# 15. Database Architecture

Suggested Supabase tables:

```text
profiles
education
experience
skills
documents
job_preferences
jobs
job_matches
applications
application_events
notifications
```

## profiles

```text
id
user_id
name
email
phone
location
address
linkedin
github
portfolio
created_at
updated_at
```

## education

```text
id
user_id
institution
degree
branch
cgpa
graduation_year
marks_10
marks_12
```

## experience

```text
id
user_id
company
position
start_date
end_date
description
```

## skills

```text
id
user_id
skill_name
skill_type
```

## documents

```text
id
user_id
document_type
file_name
storage_path
created_at
```

## job_preferences

```text
id
user_id
job_titles
locations
skills
experience
salary_min
job_type
remote
created_at
updated_at
```

## jobs

```text
id
title
company
location
description
salary
url
source
external_job_id
posted_at
created_at
```

## job_matches

```text
id
user_id
job_id
match_score
match_reason
created_at
```

## applications

```text
id
user_id
job_id
status
application_url
applied_at
updated_at
```

## application_events

```text
id
application_id
event_type
event_description
event_date
source
```

Example events:

```text
APPLICATION_SUBMITTED
EMAIL_RECEIVED
UNDER_REVIEW
INTERVIEW_REQUESTED
REJECTED
ACCEPTED
```

## notifications

```text
id
user_id
type
title
message
is_read
created_at
```

---

# 16. Database Relationships

```text
                    users
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
      profiles    education    experience
          │
          ├──────────► skills
          │
          ├──────────► documents
          │
          └──────────► job_preferences
                              │
                              ▼
                         JOB ENGINE
                              │
                              ▼
                            jobs
                              │
                              ▼
                        job_matches
                              │
                              ▼
                        applications
                              │
                              ▼
                     application_events
```

---

# 17. Frontend Pages

Suggested pages:

```text
/login
/register
/dashboard
/jobs
/jobs/:id
/applications
/applications/:id
/history
/profile
/settings
/documents
/preferences
```

### Dashboard

Display:

```text
New Jobs
High Match Jobs
Applications
Interviews
Rejected
Accepted
Recent Activity
```

### Jobs

```text
Job Title
Company
Location
Salary
Match %
Source
Posted Date

[View Job]
[Save]
[Apply]
```

### Applications

```text
Company
Job
Applied Date
Current Status
Last Updated
```

### Profile / Apply Settings

Central place for:

```text
Personal Details
Education
Experience
Skills
Resume
Certificates
Marksheets
```

---

# 18. Background Jobs / Scheduler

Automatic searching should run in the background rather than when the user opens the website.

Example:

```text
Scheduler
   │
   ▼
Every few hours
   │
   ▼
Load active users
   │
   ▼
Read preferences
   │
   ▼
Search supported sources
   │
   ▼
Normalize + Deduplicate
   │
   ▼
Calculate Match Scores
   │
   ▼
Store New Matches
   │
   ▼
Create Notifications
```

Possible implementation:
- Scheduled backend task
- Cron
- Supabase scheduled functions
- Cloud scheduler depending on deployment

---

# 19. Security

Important rules:

### Authentication
Use Supabase Auth.

### Database
Enable Supabase Row Level Security.

Users should only be able to access:

```text
WHERE user_id = authenticated_user_id
```

### Documents
Do not expose resumes or marksheets publicly.

Use private storage and controlled access.

### API Keys
Never put API keys in frontend code.

Use:

```text
Frontend
   ↓
Backend
   ↓
Secret API Keys
```

### Gmail
Request only the permissions required by the application.

---

# 20. Recommended Development Order

Build in this order:

```text
PHASE 1
Authentication
        ↓
PHASE 2
User Profile + Apply Settings
        ↓
PHASE 3
Resume / Document Upload
        ↓
PHASE 4
Job Preferences
        ↓
PHASE 5
Job Source Integration
        ↓
PHASE 6
Job Database
        ↓
PHASE 7
Job Matching
        ↓
PHASE 8
Dashboard
        ↓
PHASE 9
Application Tracking
        ↓
PHASE 10
Gmail Integration
        ↓
PHASE 11
Assisted Application
        ↓
PHASE 12
AI Matching / Automation
```

---

# 21. MVP

The first working version should contain only:

```text
✓ Google Login
✓ User Profile
✓ Resume Upload
✓ Job Preferences
✓ Job Search
✓ Job Database
✓ Match Score
✓ Job Recommendations
✓ Application Tracking
✓ Application History
```

Do **not** start with:
- Fully automatic applications
- Complex AI
- Gmail classification
- Multiple complicated job sources
- Advanced recommendation models

Get the MVP working first.

---

# 22. Final Target

The finished platform should feel like:

```text
                    JOB FINDER
                        │
            ┌───────────┴───────────┐
            │                       │
        User Profile          Job Preferences
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
                 JOB SEARCH ENGINE
                        │
                        ▼
                JOBS FROM SOURCES
                        │
                        ▼
                 MATCH + RANK JOBS
                        │
                        ▼
                  USER DASHBOARD
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Apply          Save         Ignore
          │
          ▼
    APPLICATION
      TRACKING
          │
          ▼
    Gmail Updates
          │
          ▼
    Status Changes
          │
          ▼
       HISTORY
```

## Core Design Principle

Keep the responsibilities separated:

```text
Frontend
    → UI only

Backend
    → Business logic

Supabase
    → Auth + Database + File Storage

Job Engine
    → Search + Normalize + Match

Gmail Integration
    → Application email detection

Application Module
    → Assisted application workflow
```

This separation will make the project much easier to develop, debug, and extend.
