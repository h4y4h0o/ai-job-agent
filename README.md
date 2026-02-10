# AI Job Application Agent

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

An intelligent job search assistant that uses AI to analyze job postings and match them with your CV.


## What it does

- ⚙️ Searches for jobs daily across multiple job boards using Adzuna API
- 🤖 AI-powered job fit analysis using Claude API
- 📊 Scoring system (0-100) for job-candidate matching and filters results to show only relevant opportunities (≥65% match)
- 🎯 Identifies matching and missing skills
- 💡 Provides personalized application recommendations
- 📝 Generate cover letter for the recommended jobs
- 📧 Emails you daily with top matches and detailed recommendations
- 📈 Displays results in a beautiful web dashboard with statistics
- 🔄 RESTful API for easy integration


## 🚀 Features

### ✅ Automated Job Discovery
- Searches multiple job titles simultaneously
- Configurable search criteria (location, keywords)
- Daily automated execution via n8n scheduler

### ✅ AI-Powered Analysis
- Claude AI analyzes each job description
- Compares against your CV automatically
- Calculates 4-component fit score
- Identifies matching and missing skills

### ✅ Smart Filtering
- Only shows jobs ≥65% fit score
- Priority categorization (High/Medium/Low)
- "Should Apply" recommendations

### ✅ Rich Notifications
- Daily email digest with top matches
- Score breakdowns and skill analysis
- Direct links to job postings
- AI-generated application recommendations

### ✅ Visual Dashboard
- Real-time statistics and trends
- Sortable job cards with full details
- Skills gap analysis
- Mobile-responsive design


## 📸 Screenshots

### 🔄 n8n Automation Workflow
![n8n Workflow](screenshots/n8n-workflow.png)
*Complete automation pipeline: search → analyze → filter → notify*

### 📧 Email Notification
![Email Digest](screenshots/email.png)
*Daily email with top job matches and AI recommendations*

### 📊 Dashboard View
![AI Job Agent Dashboard](screenshots/dashboard2.png)
*Real-time job matching dashboard with statistics, scores, and skill analysis*


## 🛠️ Tech Stack

**Backend:**
- Python 3.x
- Flask (API & Dashboard)
- Claude AI (Anthropic API)
- SQLite (n8n data)

**Automation:**
- n8n (Workflow orchestration)
- Docker (n8n containerization)

**APIs:**
- Adzuna API (Job search)
- Anthropic Claude API (AI analysis)
- Gmail API (Notifications)

**Frontend:**
- Jinja2 Templates
- Custom CSS (No frameworks)
- Responsive design


## Project Status

### Completed:
- ✅ Development environment setup
- ✅ Flask API with job analysis endpoint
- ✅ Claude AI integration
- ✅ CV parsing and comparison logic
- ✅ Job search automation with Adzuna API
- ✅ n8n workflow automation
  - Scheduled job searches
  - Automated AI analysis
  - Job filtering by fit score
  - Results aggregation
  - Email notifications
- ✅ Dashboard to visualize job matches


## 🤖 How It Works
```
┌─────────────┐
│   n8n       │  Scheduler (runs daily)
└──────┬──────┘
       │
       ├──────────────────────────────┐
       │                              │
       ▼                              ▼
┌──────────────┐           ┌─────────────────┐
│ job_searcher │           │   Flask API     │
│ Adzuna API   ├──jobs────▶│   Claude AI     │
└──────────────┘           └────────┬────────┘
                                    │
                                    │ analysis
                                    ▼
                          ┌─────────────────┐
                          │  Filter (≥65)   │
                          │  Save results   │
                          │  Send email     │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   Dashboard     │
                          │  Visualize      │
                          └─────────────────┘
```


## 📊 Components

### 1. Flask API (`app.py`) - Port 5000
- Analyzes job postings against your CV using Claude AI
- Calculates comprehensive fit scores (0-100)
- Provides skill matching and gap analysis
- Generates personalized recommendations

**Scoring System:**
- Skills Match (40 points): Technical skills alignment
- Experience Level (30 points): Seniority fit
- Domain/Industry (20 points): Relevant domain knowledge
- Other Factors (10 points): Location, culture fit, etc.

### 2. n8n Workflow Automation - Port 5678
Complete automated pipeline with 12+ nodes:
- **Adzuna API Integration**: Searches 20+ jobs daily
- **Job Analysis Loop**: Processes each job through AI
- **Intelligent Filtering**: Only jobs scoring ≥65%
- **Data Aggregation**: Combines and sorts results
- **Email Generation**: Beautiful HTML emails with details
- **Gmail Integration**: Automatic daily notifications

### 3. Web Dashboard (`dashboard.py`) - Port 5001
Beautiful, responsive web interface featuring:
- **Statistics Overview**: Total matches, average scores, priority breakdown
- **Job Cards**: Detailed view with scores, skills, recommendations
- **Skills Analysis**: Matching vs. missing skills visualization
- **Priority Badges**: High/Medium/Low color-coded indicators: Green (75+), Yellow (65-74), Red (<65)
- **Top Skills**: Most in-demand skills you should learn


## Setup Instructions

### Prerequisites
- Python 3.11+
- Anthropic API key
- Adzuna API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/job-agent.git
cd job-agent
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install flask langchain langchain-anthropic python-dotenv requests
```

4. Create `.env` file with your API keys
```bash
ANTHROPIC_API_KEY=your_key_here
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_adzuna_key
```

5. Create your CV file (`my_cv.txt`)

6. Configure job search

Edit `search_config.json` with your job preferences:
```json
{
  "job_title": "AI Engineer",
  "location": "London",
  "max_results": 20
}
```

7. Run the Flask API
```bash
python app.py
```

API runs at: http://127.0.0.1:5000

8. Start the Dashboard
```bash
python3 dashboard.py
```

Dashboard runs at: http://127.0.0.1:5001

9. Run job search
```bash
python3 job_searcher.py
```

10. Start n8n (optional - for automation)
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Access n8n at: http://localhost:5678


## API Endpoints

### Health Check
```bash
GET http://127.0.0.1:5000/health
```

### Analyze Job Fit
```bash
POST http://127.0.0.1:5000/analyze-fit
Content-Type: application/json

{
  "job_title": "Data Scientist",
  "company": "Company Name",
  "location": "Paris",
  "job_description": "Job description text...",
  "job_url": "https://..."
}
```

## Example Response
```json
{
  "overall_score": 85,
  "breakdown": {
    "skills_match": 35,
    "experience_level": 28,
    "domain_industry": 18,
    "other_factors": 4
  },
  "matching_skills": ["Python", "SQL", "Machine Learning"],
  "missing_skills": ["AWS", "Docker"],
  "recommendation": "Strong fit! Apply immediately.",
  "priority": "High",
  "should_apply": true
}
```

### Get Jobs (Dashboard API)
```bash
GET http://127.0.0.1:5001/api/jobs
```

### Get Statistics (Dashboard API)
```bash
GET http://127.0.0.1:5001/api/stats
```


## 📊 Sample Output

The AI analysis returns:
```json
{
  "fit_score": 82,
  "matching_skills": ["Python", "Machine Learning", "Flask"],
  "missing_skills": ["Kubernetes", "TensorFlow"],
  "recommendation": "Strong match! Your Python and ML skills align well."
}
```

## 📁 Project Structure
```
ai-job-agent/
├── app.py                  # Flask API for job analysis
├── job_searcher.py         # Adzuna job search script
├── dashboard.py            # Web dashboard
├── templates/
│   └── dashboard.html      # Dashboard UI
├── search_config.json      # Job search parameters
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
└── README.md              # This file

# Not tracked in Git (privacy):
├── my_cv.txt              # Your CV (create this)
├── job_results.json       # Search results (generated)
└── .env                   # Your API keys (create this)
```


## 🔒 Security Notes

- **Never commit `.env` file** - Contains sensitive API keys
- **Never commit `my_cv.txt`** - Contains personal information
- **Never commit `job_results.json`** - Contains real job data
- All sensitive files are in `.gitignore`


## License

MIT License - Feel free to use this for your own projects!

## Contact

Created by Zahra Vahidi Ferdousi - zahra.vahidiferdousi@gmail.com - https://www.linkedin.com/in/zahra-vahidi-ferdousi/

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Job data from [Adzuna API](https://developer.adzuna.com/)
- Inspired by the need to make job searching less painful! 😊
