from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# Lazy initialization - avoids crash if GROQ_API_KEY not set at import time
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def load_cv():
    """Load CV content"""
    cv_path = os.path.join(os.path.dirname(__file__), "my_cv.txt")
    with open(cv_path, "r") as f:
        return f.read()


def detect_language(text):
    """Detect if text is primarily French or English"""
    french_indicators = ["nous", "recherchons", "poste", "vous", "entreprise", "équipe"]
    english_indicators = ["we", "looking", "position", "you", "company", "team"]

    text_lower = text.lower()
    french_count = sum(1 for word in french_indicators if word in text_lower)
    english_count = sum(1 for word in english_indicators if word in text_lower)

    return "fr" if french_count > english_count else "en"


def generate_cover_letter(job_data, cv_content=None, language="fr"):
    """
    Generate tailored cover letter for a specific job.

    Args:
        job_data: dict with job_title, company, job_description, matching_skills, missing_skills
        cv_content: optional CV text (loads from file if not provided)
        language: 'fr' for French or 'en' for English (default: 'fr')

    Returns:
        dict with cover_letter text and metadata
    """
    if cv_content is None:
        cv_content = load_cv()

    # Debug: Print what language was received
    print(f"\n{'='*60}")
    print(f"🔍 Language parameter received: '{language}' (type: {type(language)})")
    print(f"{'='*60}\n")

    # English prompt
    prompt_en = f"""You are a professional career coach helping write an excellent cover letter IN ENGLISH.

    CANDIDATE CV:
    {cv_content}

    JOB POSTING:
    Position: {job_data['job_title']}
    Company: {job_data['company']}
    Description: {job_data.get('job_description', 'Not provided')}

    ANALYSIS:
    Matching Skills: {', '.join(job_data.get('matching_skills', []))}
    Skills to Highlight: {', '.join(job_data.get('missing_skills', [])[:3])}

    CRITICAL: Write this cover letter ONLY in ENGLISH. Do NOT use French.

    Write a compelling, personalized cover letter IN ENGLISH that:
    1. Shows genuine interest in {job_data['company']} and this specific role
    2. Highlights the candidate's most relevant experience and skills
    3. Addresses how they can contribute despite any skill gaps
    4. Uses a professional but warm tone
    5. Is 250-350 words (3-4 paragraphs)
    6. Avoids clichés and generic statements

    Structure:
    - Opening: Hook and why this role/company
    - Body: 2 key experiences/skills that make them a great fit
    - Closing: Enthusiasm and call to action

    REMINDER: Return ONLY the cover letter text IN ENGLISH, no additional commentary."""

    # French prompt
    prompt_fr = f"""Tu es un conseiller en carrière professionnel aidant à rédiger une excellente lettre de motivation EN FRANÇAIS.

    CV DU CANDIDAT:
    {cv_content}

    OFFRE D'EMPLOI:
    Poste: {job_data['job_title']}
    Entreprise: {job_data['company']}
    Description: {job_data.get('job_description', 'Non fournie')}

    ANALYSE:
    Compétences correspondantes: {', '.join(job_data.get('matching_skills', []))}
    Compétences à mettre en avant: {', '.join(job_data.get('missing_skills', [])[:3])}

    CRITIQUE: Écris cette lettre UNIQUEMENT en FRANÇAIS. N'utilise PAS l'anglais.

    Rédige une lettre de motivation convaincante et personnalisée EN FRANÇAIS qui:
    1. Montre un intérêt sincère pour {job_data['company']} et ce poste spécifique
    2. Met en avant les expériences et compétences les plus pertinentes du candidat
    3. Explique comment il peut contribuer malgré les lacunes de compétences
    4. Utilise un ton professionnel mais chaleureux
    5. Fait 250-350 mots (3-4 paragraphes)
    6. Évite les clichés et déclarations génériques

    Structure:
    - Ouverture: Accroche et pourquoi ce rôle/cette entreprise
    - Corps: 2 expériences/compétences clés qui en font un excellent candidat
    - Clôture: Enthousiasme et appel à l'action

    RAPPEL: Retourne UNIQUEMENT le texte de la lettre de motivation EN FRANÇAIS, sans commentaire additionnel.
    La lettre doit commencer par "Madame, Monsieur," ou "À l'attention du service recrutement,"."""

    # Select prompt based on language
    if language and str(language).lower() == "en":
        prompt = prompt_en
        print("✅ Selected ENGLISH prompt")
    else:
        prompt = prompt_fr
        print("✅ Selected FRENCH prompt")

    try:
        response = _get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        cover_letter_text = response.choices[0].message.content.strip()

        # Detect actual language of generated text
        first_words = cover_letter_text[:100].lower()
        is_french = any(
            word in first_words
            for word in ["madame", "monsieur", "votre", "entreprise"]
        )
        is_english = any(
            word in first_words for word in ["dear", "hiring", "manager", "position"]
        )

        actual_language = "fr" if is_french else ("en" if is_english else language)

        print(f"📝 Generated {len(cover_letter_text)} characters")
        print(f"🌍 Requested: {language}, Detected in output: {actual_language}")

        return {
            "cover_letter": cover_letter_text,
            "generated_at": datetime.now().isoformat(),
            "job_title": job_data["job_title"],
            "company": job_data["company"],
            "word_count": len(cover_letter_text.split()),
            "language": actual_language,
        }

    except Exception as e:
        print(f" Error generating cover letter: {e}")
        return None


def save_cover_letter(cover_letter_data, filename=None):
    """Save cover letter to file"""
    if filename is None:
        safe_company = cover_letter_data["company"].replace(" ", "_").replace("/", "_")
        safe_title = cover_letter_data["job_title"].replace(" ", "_").replace("/", "_")
        filename = f"cover_letter_{safe_company}_{safe_title}.txt"

    filepath = os.path.join(os.path.dirname(__file__), "cover_letters", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        f.write(
            f"Cover Letter for {cover_letter_data['job_title']} at {cover_letter_data['company']}\n"
        )
        f.write(f"Generated: {cover_letter_data['generated_at']}\n")
        f.write(f"Word Count: {cover_letter_data['word_count']}\n")
        f.write("\n" + "=" * 80 + "\n\n")
        f.write(cover_letter_data["cover_letter"])

    print(f"✅ Cover letter saved: {filepath}")
    return filepath


# Test function
if __name__ == "__main__":
    # Test with sample job
    test_job = {
        "job_title": "Senior Data Scientist",
        "company": "TechCorp",
        "job_description": "Looking for a data scientist with Python, ML, and cloud experience...",
        "matching_skills": ["Python", "Machine Learning", "SQL", "Data Analysis"],
        "missing_skills": ["AWS", "Spark", "Kubernetes"],
    }

    print("🔄 Generating cover letter...")
    result = generate_cover_letter(test_job)

    if result:
        print("\n" + "=" * 80)
        print(result["cover_letter"])
        print("=" * 80)
        print(f"\n📊 Word count: {result['word_count']}")

        # Save it
        save_cover_letter(result)
