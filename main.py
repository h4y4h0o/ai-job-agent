"""
Combined Flask app for Railway deployment.
Merges API (app.py) + Dashboard (dashboard.py) into a single server.
"""

from flask import Flask, request, jsonify, render_template
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import json
import hashlib
from datetime import datetime
from collections import Counter

from cover_letter_generator import generate_cover_letter, save_cover_letter

load_dotenv()

app = Flask(__name__)

CACHE = {}

# Lazy initialization - avoids crash if keys not set at import time
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )
    return _llm


def get_cv():
    cv_content = os.getenv("CV_CONTENT")
    if cv_content:
        return cv_content
    cv_path = os.path.join(os.path.dirname(__file__), "my_cv.txt")
    if os.path.exists(cv_path):
        with open(cv_path, "r", encoding="utf-8") as f:
            return f.read()
    return "CV not configured. Set CV_CONTENT environment variable."

# Job results file path
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "job_results.json")

# Fit analysis prompt template
FIT_ANALYSIS_PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert career advisor analyzing job fit.

CANDIDATE CV:
{cv}

JOB POSTING:
Title: {job_title}
Company: {company}
Location: {location}
Description: {job_description}

Analyze the fit between this candidate and job. Provide:

1. **Overall Fit Score** (0-100):
   - 90-100: Excellent fit, apply immediately
   - 75-89: Very good fit, strong candidate
   - 65-74: Good fit, worth applying
   - 50-64: Moderate fit, apply if interested
   - Below 50: Poor fit, skip

2. **Breakdown**:
   - Skills Match (0-40 points): Which required skills does candidate have?
   - Experience Level (0-30 points): Does experience match seniority level?
   - Domain/Industry (0-20 points): Relevant industry experience?
   - Other Factors (0-10 points): Location, company culture fit, etc.

3. **Matching Skills**: List skills from CV that match job requirements

4. **Missing Skills**: List required skills candidate doesn't have

5. **Recommendation**: Should they apply? Why or why not?

6. **Application Priority**: High/Medium/Low

Return ONLY valid JSON in this exact format:
{{
  "overall_score": 85,
  "breakdown": {{
    "skills_match": 35,
    "experience_level": 25,
    "domain_industry": 18,
    "other_factors": 7
  }},
  "matching_skills": ["Python", "Machine Learning", "SQL"],
  "missing_skills": ["AWS", "Kubernetes"],
  "recommendation": "Strong candidate. Your ML and Python experience align well...",
  "priority": "High",
  "should_apply": true
}}
"""
)


# ============================================================
# API ENDPOINTS (from app.py)
# ============================================================


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "message": "Job Agent API is running"})


@app.route("/analyze-fit", methods=["POST"])
def analyze_fit():
    try:
        data = request.json

        cache_key = hashlib.md5(
            f"{data['job_title']}{data['company']}".encode()
        ).hexdigest()

        if cache_key in CACHE:
            print(f"Using cached analysis for {data['job_title']}")
            return jsonify(CACHE[cache_key])

        required_fields = ["job_title", "company", "job_description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        prompt_text = FIT_ANALYSIS_PROMPT.format(
            cv=get_cv(),
            job_title=data["job_title"],
            company=data["company"],
            location=data.get("location", "Not specified"),
            job_description=data["job_description"],
        )

        print(f"Analyzing: {data['job_title']} at {data['company']}")
        response = get_llm().invoke(prompt_text)
        response_text = response.content

        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]
        analysis = json.loads(json_str)

        analysis["job_data"] = {
            "title": data["job_title"],
            "company": data["company"],
            "location": data.get("location"),
            "url": data.get("job_url"),
        }

        print(f"Score: {analysis['overall_score']}/100")
        CACHE[cache_key] = analysis
        return jsonify(analysis)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return jsonify({"error": "Failed to parse AI response", "details": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["GET"])
def test():
    sample_job = {
        "job_title": "Junior Data Scientist",
        "company": "Tech Startup Paris",
        "location": "Paris, France",
        "job_description": """
        We are looking for a Junior Data Scientist to join our team.
        Requirements:
        - Bachelor's or Master's degree in Computer Science, Statistics, or related field
        - 1-2 years of experience in data analysis
        - Strong Python programming skills
        - Experience with pandas, numpy, scikit-learn
        - Knowledge of SQL databases
        - Good communication skills in English
        Nice to have:
        - Experience with machine learning projects
        - Knowledge of deep learning frameworks (TensorFlow, PyTorch)
        - French language skills
        """,
        "job_url": "https://example.com/job/123",
    }
    from flask import current_app

    with current_app.test_request_context(json=sample_job, method="POST"):
        return analyze_fit()


@app.route("/save-results", methods=["POST"])
def save_results():
    try:
        data = request.json
        with open(RESULTS_FILE, "w") as f:
            json.dump(data, f, indent=2)

        jobs_count = 0
        if isinstance(data, list) and len(data) > 0:
            if "data" in data[0]:
                jobs_count = len(data[0]["data"])

        print(f"Saved {jobs_count} jobs to {RESULTS_FILE}")
        return jsonify({"status": "success", "message": f"Saved {jobs_count} jobs", "filepath": RESULTS_FILE})
    except Exception as e:
        print(f"Error saving results: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/generate-cover-letter", methods=["POST"])
def api_generate_cover_letter():
    try:
        data = request.json
        language = data.get("language", "fr")
        result = generate_cover_letter(data, language=language)

        if result:
            if data.get("save", False):
                filepath = save_cover_letter(result)
                result["filepath"] = filepath
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to generate cover letter"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# DASHBOARD ENDPOINTS (from dashboard.py)
# ============================================================


def load_job_data():
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r") as f:
                data = json.load(f)

            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict) and "json" in first_item:
                    inner_data = first_item["json"]
                    if isinstance(inner_data, dict) and "data" in inner_data:
                        jobs = inner_data["data"]
                        print(f"Loaded {len(jobs)} jobs from file")
                        return jobs
                elif isinstance(first_item, dict) and "data" in first_item:
                    jobs = first_item["data"]
                    print(f"Loaded {len(jobs)} jobs from file")
                    return jobs
                elif isinstance(first_item, dict) and "overall_score" in first_item:
                    print(f"Loaded {len(data)} jobs from file")
                    return data

            print("Couldn't parse job data structure")
            return []
        else:
            print(f"File doesn't exist: {RESULTS_FILE}")
            return []
    except Exception as e:
        print(f"Error loading job data: {e}")
        return []


def calculate_statistics(jobs):
    if not jobs:
        return {
            "total_jobs": 0, "avg_score": 0, "high_priority": 0,
            "medium_priority": 0, "low_priority": 0, "avg_skills_match": 0,
        }

    scores = [job.get("overall_score", 0) for job in jobs if "overall_score" in job]
    skills_scores = [job.get("skills_match_score", 0) for job in jobs]
    avg_skills_raw = sum(skills_scores) / len(skills_scores) if skills_scores else 0
    avg_skills_percent = (avg_skills_raw / 40) * 100

    return {
        "total_jobs": len(jobs),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "high_priority": len([s for s in scores if s >= 75]),
        "medium_priority": len([s for s in scores if 65 <= s < 75]),
        "low_priority": len([s for s in scores if s < 65]),
        "avg_skills_match": round(avg_skills_percent, 1),
    }


def extract_skills(jobs):
    all_skills = []
    for job in jobs:
        if "missing_skills" in job:
            all_skills.extend(job["missing_skills"])
    skill_counts = Counter(all_skills)
    return skill_counts.most_common(10)


def get_top_missing_skills(jobs, top_n=10):
    if not jobs:
        return []
    all_missing = []
    for job in jobs:
        missing = job.get("missing_skills", [])
        if missing:
            all_missing.extend(missing)
    skill_counts = Counter(all_missing)
    return skill_counts.most_common(top_n)


@app.route("/")
def index():
    jobs = load_job_data()
    stats = calculate_statistics(jobs)
    top_skills = extract_skills(jobs)
    top_missing = get_top_missing_skills(jobs)
    jobs_sorted = sorted(jobs, key=lambda x: x.get("overall_score", 0), reverse=True)

    return render_template(
        "dashboard.html",
        jobs=jobs_sorted,
        stats=stats,
        top_skills=top_skills,
        top_missing=top_missing,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.route("/api/jobs")
def api_jobs():
    jobs = load_job_data()
    return jsonify(jobs)


@app.route("/api/stats")
def api_stats():
    jobs = load_job_data()
    stats = calculate_statistics(jobs)
    return jsonify(stats)


@app.route("/dashboard/generate-cover-letter/<int:job_index>")
def dashboard_generate_cover_letter(job_index):
    """Generate cover letter for a specific job (called from dashboard)"""
    jobs = load_job_data()

    if job_index >= len(jobs):
        return jsonify({"error": "Job not found"}), 404

    job = jobs[job_index]
    language = request.args.get("language", "fr")

    # Call the function directly instead of HTTP request
    result = generate_cover_letter(
        {
            "job_title": job["title"],
            "company": job["company"],
            "job_description": job.get("description", ""),
            "matching_skills": job["matching_skills"],
            "missing_skills": job["missing_skills"],
        },
        language=language,
    )

    if result:
        save_cover_letter(result)
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to generate"}), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Job Agent on port {port}")
    app.run(host="0.0.0.0", port=port)
