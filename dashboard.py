from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# Path to job results from n8n workflow
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "job_results.json")


def load_job_data():
    """Load job results from JSON file"""
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r") as f:
                data = json.load(f)

                # Handle the structure: [{"json": {"data": [jobs]}}]
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]

                    # Check if wrapped in 'json' key
                    if isinstance(first_item, dict) and "json" in first_item:
                        inner_data = first_item["json"]

                        # Now check if 'data' key exists
                        if isinstance(inner_data, dict) and "data" in inner_data:
                            jobs = inner_data["data"]
                            print(f"✅ Loaded {len(jobs)} jobs from file")
                            return jobs

                    # Fallback: Check if 'data' is directly in first item
                    elif isinstance(first_item, dict) and "data" in first_item:
                        jobs = first_item["data"]
                        print(f"✅ Loaded {len(jobs)} jobs from file")
                        return jobs

                    # Fallback: Direct array of jobs
                    elif isinstance(first_item, dict) and "overall_score" in first_item:
                        print(f"✅ Loaded {len(data)} jobs from file")
                        return data

                print("⚠️  Couldn't parse job data structure")
                return []
        else:
            print(f"⚠️  File doesn't exist: {RESULTS_FILE}")
            return []
    except Exception as e:
        print(f"❌ Error loading job data: {e}")
        import traceback

        traceback.print_exc()
        return []


def calculate_statistics(jobs):
    """Calculate summary statistics from job data"""
    if not jobs:
        return {
            "total_jobs": 0,
            "avg_score": 0,
            "high_matches": 0,
            "medium_matches": 0,
            "low_matches": 0,
        }

    scores = [job.get("overall_score", 0) for job in jobs if "overall_score" in job]

    return {
        "total_jobs": len(jobs),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "high_matches": len([s for s in scores if s >= 75]),
        "medium_matches": len([s for s in scores if 65 <= s < 75]),
        "low_matches": len([s for s in scores if s < 65]),
    }


def extract_skills(jobs):
    """Extract most common required skills"""
    all_skills = []
    for job in jobs:
        if "missing_skills" in job:
            all_skills.extend(job["missing_skills"])

    skill_counts = Counter(all_skills)
    return skill_counts.most_common(10)


@app.route("/")
def index():
    """Main dashboard page"""
    jobs = load_job_data()
    stats = calculate_statistics(jobs)
    top_skills = extract_skills(jobs)

    # Sort jobs by fit score (highest first)
    jobs_sorted = sorted(jobs, key=lambda x: x.get("overall_score", 0), reverse=True)

    return render_template(
        "dashboard.html",
        jobs=jobs_sorted,
        stats=stats,
        top_skills=top_skills,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.route("/api/jobs")
def api_jobs():
    """API endpoint for job data"""
    jobs = load_job_data()
    return jsonify(jobs)


@app.route("/api/stats")
def api_stats():
    """API endpoint for statistics"""
    jobs = load_job_data()
    stats = calculate_statistics(jobs)
    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
