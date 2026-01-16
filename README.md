# AI Job Application Agent

An intelligent job search assistant that uses AI to analyze job postings and match them with your CV.

## Features

- 🤖 AI-powered job fit analysis using Claude API
- 📊 Scoring system (0-100) for job-candidate matching
- 🎯 Identifies matching and missing skills
- 💡 Provides personalized application recommendations
- 🔄 RESTful API for easy integration

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Anthropic Claude API, LangChain
- **Automation:** n8n (coming soon)
- **APIs:** Adzuna Job Search API

## Project Status

🚧 **In Development** - Week 1, Day 2 Complete

### Completed:
- ✅ Development environment setup
- ✅ Flask API with job analysis endpoint
- ✅ Claude AI integration
- ✅ CV parsing and comparison logic

### In Progress:
- 🔄 Job search automation (Day 3)
- 🔄 n8n workflow integration (Day 4)
- 🔄 Dashboard interface (Day 5)

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

6. Run the API
```bash
python app.py
```

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

## Learning Journey

This project is part of an 8-week AI agent development learning plan. Follow along:
- Week 1-3: Job Application Agent
- Week 4-5: Data Analyst Agent
- Week 6-8: Advanced Multi-Agent Systems

## License

MIT License - Feel free to use this for your own projects!

## Contact

Created by Zahra Vahidi Ferdousi - https://www.linkedin.com/in/zahra-vahidi-ferdousi/ - zahra.vahidiferdousi@gmail.com

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Job data from [Adzuna API](https://developer.adzuna.com/)
- Inspired by the need to make job searching less painful! 😊
