"""
Job Searcher - Automated job search using Adzuna API
"""

import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()


class JobSearcher:
    """Searches for jobs using Adzuna API"""

    def __init__(self):
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID")
        self.adzuna_api_key = os.getenv("ADZUNA_API_KEY")

        if not self.adzuna_app_id or not self.adzuna_api_key:
            raise ValueError("Missing Adzuna API credentials in .env file!")

        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        print(f"✅ JobSearcher initialized with app_id: {self.adzuna_app_id[:8]}...")

    def search_adzuna(self, job_title, location, max_results=20, country="fr"):
        """
        Search jobs on Adzuna

        Args:
            job_title: Job title to search for (e.g., "Data Scientist")
            location: Location to search in (e.g., "Paris")
            max_results: Maximum number of results to return
            country: Country code (fr, us, gb, etc.)

        Returns:
            List of job dictionaries
        """

        url = f"{self.base_url}/{country}/search/1"

        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_api_key,
            "results_per_page": min(max_results, 50),  # Max 50
            "what": job_title,
            "where": location,
            "content-type": "application/json",
        }

        try:
            print(f"🔍 Searching: {job_title} in {location}...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for result in data.get("results", []):
                job = {
                    "job_title": result.get("title", ""),
                    "company": result.get("company", {}).get("display_name", "Unknown"),
                    "location": result.get("location", {}).get(
                        "display_name", location
                    ),
                    "job_description": result.get("description", ""),
                    "job_url": result.get("redirect_url", ""),
                    "salary_min": result.get("salary_min"),
                    "salary_max": result.get("salary_max"),
                    "created_date": result.get("created"),
                    "source": "Adzuna",
                    "category": result.get("category", {}).get("label", ""),
                }
                jobs.append(job)

            print(f"   ✅ Found {len(jobs)} jobs")
            return jobs

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error searching Adzuna: {e}")
            return []
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return []

    def search_all_criteria(self, config_file="search_config.json"):
        """
        Search all job titles and locations from config file

        Args:
            config_file: Path to JSON config with job_titles and locations

        Returns:
            List of unique jobs
        """

        # Check if config file exists
        if not os.path.exists(config_file):
            print(f"❌ Config file not found: {config_file}")
            print("Creating default config...")
            self._create_default_config(config_file)

        # Load config
        with open(config_file, "r") as f:
            config = json.load(f)

        print("=" * 60)
        print(f"🚀 Starting Job Search")
        print(f"   Job Titles: {', '.join(config['job_titles'])}")
        print(f"   Locations: {', '.join(config['locations'])}")
        print("=" * 60)

        all_jobs = []

        for job_title in config["job_titles"]:
            for location in config["locations"]:
                jobs = self.search_adzuna(
                    job_title=job_title,
                    location=location,
                    max_results=config.get("max_results_per_search", 20),
                )
                all_jobs.extend(jobs)

        # Remove duplicates by URL
        unique_jobs = {}
        for job in all_jobs:
            url = job.get("job_url")
            if url and url not in unique_jobs:
                unique_jobs[url] = job

        print("=" * 60)
        print(f"✅ Search Complete!")
        print(f"   Total jobs found: {len(all_jobs)}")
        print(f"   Unique jobs: {len(unique_jobs)}")
        print("=" * 60)

        return list(unique_jobs.values())

    def _create_default_config(self, config_file):
        """Create a default search configuration file"""

        default_config = {
            "job_titles": [
                "Data Scientist",
                "AI Engineer",
                "Machine Learning Engineer",
            ],
            "locations": ["Paris", "Remote"],
            "max_results_per_search": 10,
        }

        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        print(f"✅ Created default config: {config_file}")
        print("   Edit this file to customize your search!")


def main():
    """Main function to test job search"""

    print("=" * 60)
    print("🤖 AI Job Agent - Job Searcher")
    print("=" * 60)

    try:
        # Initialize searcher
        searcher = JobSearcher()

        # Search for jobs
        jobs = searcher.search_all_criteria()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobs_found_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        # Also save as job_results.json for n8n workflow
        with open('job_results.json', 'w') as f:
            json.dump(jobs, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")

        # Show sample jobs
        if jobs:
            print("\n📋 Sample Jobs:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job['job_title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                salary = (
                    f"€{job['salary_min']:,.0f} - €{job['salary_max']:,.0f}"
                    if job["salary_min"]
                    else "Not specified"
                )
                print(f"   Salary: {salary}")
                print(f"   URL: {job['job_url'][:60]}...")

        print("\n" + "=" * 60)
        print("✅ Job search complete!")
        print(f"   Next: Run analysis on these jobs with your Flask API")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
