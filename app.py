# Import statements - these load the tools we need
from flask import Flask, request, jsonify
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq  # Changed from langchain_anthropic

# from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import json
import hashlib

from cover_letter_generator import generate_cover_letter, save_cover_letter

# Flask: Creates web server
# request, jsonify: Handle incoming data and send JSON responses
# ChatAnthropic: Connects to Claude API
# PromptTemplate: Formats instructions for Claude
# os: Access environment variables
# load_dotenv: Load keys from .env file
# json: Work with JSON data

CACHE = {}

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Initialize Claude
# llm = ChatAnthropic(
#    model="claude-sonnet-4-20250514",  # Which Claude model to use
#    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),  # Your API key
#    temperature=0,  # 0 = consistent, 1 = creative
# )

# Initialize Groq
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Which Groq model to use
    groq_api_key=os.getenv("GROQ_API_KEY"),  # Your API key
    temperature=0,  # 0 = consistent, 1 = creative
)

# Read your CV file
with open("my_cv.txt", "r", encoding="utf-8") as f:
    USER_CV = f.read()

print(f"✅ CV loaded: {len(USER_CV)} characters")

# This is the "recipe" we give Claude for analyzing jobs
# FIT_ANALYSIS_PROMPT = PromptTemplate.from_template(
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


# Create API Endpoints (a specific address the web server listens to)
@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint - just confirms the server is running
    Test with: curl http://localhost:5000/health
    """
    return jsonify({"status": "healthy", "message": "Job Agent API is running"})


# Main endpoint to analyze job fit
@app.route("/analyze-fit", methods=["POST"])
def analyze_fit():
    """
    Main endpoint - analyzes job fit

    Expects JSON with:
    - job_title
    - company
    - location
    - job_description
    - job_url

    Returns: Fit analysis in JSON format
    """
    try:
        # Get the data sent to us
        data = request.json

        # Create cache key (to prevent re-analyzing the same job twice)
        cache_key = hashlib.md5(
            f"{data['job_title']}{data['company']}".encode()
        ).hexdigest()

        # Check cache
        if cache_key in CACHE:
            print(f"✅ Using cached analysis for {data['job_title']}")
            return jsonify(CACHE[cache_key])

        # Check if required fields are present
        required_fields = ["job_title", "company", "job_description"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"error": f"Missing required field: {field}"}),
                    400,
                )  # 400 = Bad Request

        # Create the prompt by filling in the template
        prompt_text = FIT_ANALYSIS_PROMPT.format(
            cv=USER_CV,
            job_title=data["job_title"],
            company=data["company"],
            location=data.get("location", "Not specified"),
            job_description=data["job_description"],
        )

        print(f"🤔 Analyzing: {data['job_title']} at {data['company']}")

        # Ask Claude to analyze
        response = llm.invoke(prompt_text)

        # Extract the JSON from Claude's response
        response_text = response.content

        # Find the JSON part (Claude sometimes adds text before/after)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]

        # Parse the JSON string into a Python dictionary
        analysis = json.loads(json_str)

        # Add the original job info to the response
        analysis["job_data"] = {
            "title": data["job_title"],
            "company": data["company"],
            "location": data.get("location"),
            "url": data.get("job_url"),
        }

        print(f"✅ Score: {analysis['overall_score']}/100")

        # Cache the result
        CACHE[cache_key] = analysis

        # Send back the analysis
        return jsonify(analysis)

    except json.JSONDecodeError as e:
        # If we can't parse Claude's response
        print(f"❌ JSON parsing error: {e}")
        return (
            jsonify({"error": "Failed to parse AI response", "details": str(e)}),
            500,
        )  # 500 = Server Error

    except Exception as e:
        # Any other error
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# Test endpoint with sample job
@app.route("/test", methods=["GET"])
def test():
    """
    Test endpoint with a sample job
    Just visit: curl http://127.0.0.1:5000/test
    """
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

    # Manually create the analysis
    from flask import current_app

    with current_app.test_request_context(json=sample_job, method="POST"):
        return analyze_fit()


@app.route("/save-results", methods=["POST"])
def save_results():
    """Endpoint for n8n to save job results"""
    try:
        data = request.json
        filepath = os.path.join(os.path.dirname(__file__), "job_results.json")

        # Save to file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        jobs_count = 0
        if isinstance(data, list) and len(data) > 0:
            if "data" in data[0]:
                jobs_count = len(data[0]["data"])

        print(f"✅ Saved {jobs_count} jobs to {filepath}")

        return jsonify(
            {
                "status": "success",
                "message": f"Saved {jobs_count} jobs",
                "filepath": filepath,
            }
        )
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# cover letter generation endpoint
@app.route("/generate-cover-letter", methods=["POST"])
def api_generate_cover_letter():
    """Generate cover letter for a job (French or English)"""
    try:
        data = request.json

        # Get language preference (default to French)
        language = data.get("language", "fr")

        # Generate cover letter
        result = generate_cover_letter(data, language=language)

        if result:
            # Optionally save to file
            if data.get("save", False):
                filepath = save_cover_letter(result)
                result["filepath"] = filepath

            return jsonify(result)
        else:
            return jsonify({"error": "Échec de la génération"}), 500

    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500


# Start the server
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Job Agent API Starting...")
    print("=" * 60)
    print(f"📝 CV loaded: {len(USER_CV)} characters")
    print(f"🔗 Server: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health      - Check if server is running")
    print("  POST /analyze-fit - Analyze a job (requires JSON body)")
    print("  POST /test        - Test with sample job")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    # Start Flask server
    app.run(debug=True, port=5000)
