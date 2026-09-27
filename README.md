# Employee Request Automation System

An AI-powered employee request management and automation system that classifies employee requests, determines priority, routes requests to the appropriate team, tracks SLA deadlines, and automatically escalates overdue requests through Slack.

The project demonstrates an end-to-end business automation workflow using **FastAPI, OpenAI, MongoDB Atlas, n8n, and Slack**.

---

## Features

- Employee self-service request portal
- AI-powered request classification
- Automatic priority determination
- Automatic team assignment
- Dynamic SLA calculation
- Unique request/ticket IDs
- MongoDB Atlas persistence
- Admin monitoring dashboard
- Request status management
- Team-specific Slack notifications
- Automated SLA monitoring
- Daily escalation reminders for unresolved overdue requests
- Secured internal automation APIs
- n8n-based workflow orchestration

---

## System Architecture

```text
                         Employee
                            |
                            v
                   Employee Web Portal
                            |
                            v
                         FastAPI
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          OpenAI       MongoDB Atlas    n8n Webhook
       Classification                       |
                                            v
                                      Team Routing
                                            |
                                            v
                                          Slack
```

A second automation continuously monitors SLA breaches:

```text
                    n8n Schedule Trigger
                      Every 15 Minutes
                              |
                              v
                       FastAPI Internal API
                              |
                              v
                         MongoDB Atlas
                              |
                              v
                    Retrieve Overdue Tickets
                              |
                              v
                         Split Tickets
                              |
                              v
                       Route by Team
                              |
                              v
                     Slack SLA Escalation
                              |
                              v
                     Update escalated_at
```

A detailed architecture diagram is available in the `docs/` directory.

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| AI | OpenAI API |
| Database | MongoDB Atlas |
| Workflow Automation | n8n |
| Notifications | Slack |
| Public Development Tunnel | ngrok |
| API Server | Uvicorn |

---

## How It Works

### 1. Employee Request Submission

An employee submits a request through the web portal.

The request contains information such as:

- Employee name
- Employee email
- Request description

FastAPI receives the request and passes the request text to the AI classification service.

---

### 2. AI Classification

The OpenAI-powered classification layer analyzes the request and determines its:

- **Category**
- **Priority**

Supported request categories include:

- HR
- IT
- Payroll
- Operations
- Other

The application then determines the appropriate support team and SLA based on the classification result.

---

### 3. Ticket Creation

A unique ticket ID is generated for every request.

Example:

```text
REQ-2026-1DBCAB
```

The ticket is stored in MongoDB Atlas together with information such as:

```text
ticket_id
employee_name
employee_email
request_text
category
priority
assigned_team
status
sla_hours
sla_due_at
created_at
updated_at
resolved_at
is_escalated
escalated_at
```

---

## Request Lifecycle

Requests move through the following lifecycle:

```text
Open
  |
  v
Active
  |
  v
Finalized
```

When a request is finalized, its resolution timestamp is recorded.

Finalized requests are excluded from future SLA escalation processing.

---

## Admin Dashboard

The admin dashboard provides visibility into employee requests and their current state.

Administrators can:

- View submitted requests
- Inspect request details
- See category and priority
- View the assigned team
- Monitor SLA deadlines
- Identify overdue requests
- Update request status
- Finalize resolved requests

---

# Automation Workflows

The system contains two primary n8n workflows.

## Workflow 1 - New Request Routing

When FastAPI creates a request, it sends the ticket data to an n8n webhook.

```text
Employee Request
       |
       v
FastAPI
       |
       v
MongoDB
       |
       v
n8n Webhook
       |
       v
Route by Assigned Team
       |
       +----> Payroll
       |
       +----> HR
       |
       +----> IT
       |
       +----> Operations
       |
       +----> General Support
                    |
                    v
                  Slack
```

Each request is sent to the Slack channel belonging to the assigned support team.

---

## Workflow 2 - SLA Monitoring & Daily Escalation

A scheduled n8n workflow checks for overdue requests every 15 minutes.

```text
Check SLA Every 15 Minutes
           |
           v
Get Overdue Tickets
           |
           v
Split Overdue Tickets
           |
           v
Route Escalation by Assigned Team
           |
     +-----+-----+-----+------------+
     |     |     |     |            |
 Payroll   HR    IT  Operations   General
     |     |     |     |            |
     +-----+-----+-----+------------+
                       |
                       v
                 Slack Escalation
                       |
                       v
              Mark Ticket Escalated
```

The workflow uses secured FastAPI internal endpoints to retrieve and update tickets.

### Daily Escalation Logic

An overdue request receives a maximum of **one escalation notification per calendar day**.

For example:

```text
Day 1
Ticket exceeds SLA
      |
      v
Slack escalation sent
      |
      v
escalated_at updated

Same day
      |
      v
Further 15-minute checks skip the ticket

Next day
      |
      v
Still unresolved?
      |
     Yes
      |
      v
Send another escalation
```

This prevents notification spam while ensuring unresolved SLA breaches continue to receive attention.

Daily escalation boundaries are evaluated using the **Asia/Kolkata** timezone.

---

## Internal API Security

The n8n SLA workflow communicates with internal FastAPI endpoints.

Examples:

```text
GET   /api/internal/tickets/overdue
PATCH /api/internal/tickets/{ticket_id}/escalated
```

These endpoints require an internal API key through the request header:

```text
X-Internal-API-Key
```

The key is stored as an environment variable and is not committed to source control.

---

## Project Structure

```text
employee-request-system/
|
+-- app/
|   +-- config/
|   |   +-- settings.py
|   |   +-- templates.py
|   |
|   +-- database/
|   |   +-- mongodb.py
|   |
|   +-- models/
|   |   +-- ticket.py
|   |
|   +-- routes/
|   |   +-- admin.py
|   |   +-- internal.py
|   |   +-- tickets.py
|   |   +-- web.py
|   |
|   +-- schemas/
|   |   +-- ticket.py
|   |
|   +-- services/
|   |   +-- automation_service.py
|   |   +-- classification_service.py
|   |   +-- n8n_service.py
|   |   +-- ticket_service.py
|   |
|   +-- static/
|   |   +-- css/
|   |   +-- js/
|   |
|   +-- templates/
|   |   +-- base.html
|   |   +-- dashboard.html
|   |   +-- request_form.html
|   |   +-- request_success.html
|   |   +-- ticket_detail.html
|   |
|   +-- main.py
|
+-- docs/
+-- n8n/
+-- tests/
+-- .env.example
+-- .gitignore
+-- README.md
+-- requirements.txt
```

---

# Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/saiffOP/employee-request-automation-system.git
cd employee-request-automation-system
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

and provide the required credentials and configuration values.

Never commit the `.env` file.

## 5. Start FastAPI

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Admin dashboard:

```text
http://127.0.0.1:8000/admin
```

---

## n8n Workflows

Exported workflow definitions are stored in:

```text
n8n/
```

The repository contains workflows for:

1. New employee request routing
2. SLA monitoring and daily escalation

Credentials and secrets should be configured separately inside n8n and must not be committed to the repository.

---

## Security

The project follows several basic security practices:

- Secrets are stored using environment variables.
- `.env` is excluded from Git.
- MongoDB credentials are not stored in source code.
- OpenAI credentials are not stored in source code.
- Internal automation endpoints require API-key authentication.
- n8n workflow exports should not contain production credentials.

---

## Future Improvements

For a production deployment, the system could be extended with:

- User authentication
- Role-based access control
- Team-specific dashboards
- Complete ticket audit history
- SLA analytics and reporting
- Queue-based asynchronous processing
- Centralized application logging
- Monitoring and observability
- Automated integration tests
- CI/CD pipelines
- Permanent cloud deployment
- Secret-manager integration

---

## Author

**Saif Shirgaonkar**

AI / Machine Learning Engineer