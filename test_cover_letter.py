from cover_letter_generator import generate_cover_letter

test_job = {
    "job_title": "Data Scientist",
    "company": "Google",
    "job_description": "We need a data scientist with Python skills",
    "matching_skills": ["Python", "SQL"],
    "missing_skills": ["Java", "Scala"],
}

print("=" * 60)
print("TESTING ENGLISH COVER LETTER")
print("=" * 60)
result_en = generate_cover_letter(test_job, language="en")

if result_en:
    print("\nLanguage:", result_en["language"])
    print("Word count:", result_en["word_count"])
    print("\nFirst 200 characters:")
    print(result_en["cover_letter"][:200])
    print("\n")

print("=" * 60)
print("TESTING FRENCH COVER LETTER")
print("=" * 60)
result_fr = generate_cover_letter(test_job, language="fr")

if result_fr:
    print("\nLanguage:", result_fr["language"])
    print("Word count:", result_fr["word_count"])
    print("\nFirst 200 characters:")
    print(result_fr["cover_letter"][:200])
