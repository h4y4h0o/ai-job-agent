import json

sample_jobs = [
    {
        "title": "AI Engineer",
        "company": "TechCorp",
        "location": "London",
        "fit_score": 82,
        "matching_skills": ["Python", "Machine Learning", "Flask", "API Development", "Git"],
        "missing_skills": ["Kubernetes", "TensorFlow", "AWS"],
        "recommendation": "Strong match! Your Python and ML skills align well. Consider learning Kubernetes."
    },
    {
        "title": "Machine Learning Engineer",
        "company": "DataScience Ltd",
        "location": "Remote",
        "fit_score": 78,
        "matching_skills": ["Python", "Data Analysis", "LangChain", "API Integration"],
        "missing_skills": ["PyTorch", "MLOps", "Docker", "Airflow"],
        "recommendation": "Good fit. Your LangChain experience is a plus. Focus on MLOps skills."
    },
    {
        "title": "Senior Data Scientist",
        "company": "Analytics Pro",
        "location": "Manchester",
        "fit_score": 71,
        "matching_skills": ["Python", "Data Analysis", "Statistics", "Pandas"],
        "missing_skills": ["Deep Learning", "Scala", "Spark", "R"],
        "recommendation": "Decent match. Strong fundamentals, but lacking some advanced tools."
    },
    {
        "title": "AI Solutions Architect",
        "company": "CloudTech",
        "location": "London",
        "fit_score": 85,
        "matching_skills": ["Python", "LangChain", "API Design", "Claude API", "Multi-agent Systems"],
        "missing_skills": ["Azure", "Solution Architecture", "Enterprise Sales"],
        "recommendation": "Excellent match! Your agent development skills are exactly what they need!"
    }
]

with open('job_results.json', 'w') as f:
    json.dump(sample_jobs, f, indent=2)

print("✅ Sample data created!")
