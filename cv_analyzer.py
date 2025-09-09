"""
Enhanced CV Analysis with OpenAI
Provides comprehensive candidate analysis including summaries, skills extraction, 
and structured scoring for ranking candidates.
"""
import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import logging

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CVAnalysis:
    """Structured CV analysis result"""
    source_file: str
    candidate_name: str
    current_title: str
    total_years: float
    relevant_years: float
    summary: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    experience_highlights: List[str]
    strengths: List[str]
    confidence_notes: str

def to_dict(analysis: CVAnalysis) -> dict:
    """Convert CVAnalysis to dictionary"""
    return {
        "source_file": analysis.source_file,
        "candidate_name": analysis.candidate_name,
        "current_title": analysis.current_title,
        "total_years": analysis.total_years,
        "relevant_years": analysis.relevant_years,
        "summary": analysis.summary,
        "must_have_skills": analysis.must_have_skills,
        "nice_to_have_skills": analysis.nice_to_have_skills,
        "experience_highlights": analysis.experience_highlights,
        "strengths": analysis.strengths,
        "confidence_notes": analysis.confidence_notes,
    }

def analyze_cv_with_openai(cv_text: str, filename: str, job_context: Dict[str, Any]) -> CVAnalysis:
    """
    Analyze CV using OpenAI with comprehensive job-specific insights
    """
    print(f"🤖 Starting AI analysis for: {filename} (CV text: {len(cv_text)} chars)")
    
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not openai_key:
        logging.warning("OpenAI API key not found, using fallback analysis")
        print(f"⚠️  No OpenAI key found, using fallback for: {filename}")
        return fallback_analysis(cv_text, filename, job_context)
    
    try:
        client = OpenAI(api_key=openai_key)
        
        # Enhanced prompt for comprehensive analysis
        prompt = f"""
You are an expert HR analyst and recruiter. Analyze the following CV against the provided job requirements and provide detailed insights.

JOB CONTEXT:
Job Title: {job_context.get('job_title', 'Not specified')}
Job Description: {job_context.get('job_description', 'Not specified')}

CV TEXT:
{cv_text}

Please provide a comprehensive analysis in the following JSON format:

{{
    "candidate_name": "Full name of the candidate (extract from CV)",
    "current_title": "Current or most recent job title",
    "total_years": 0.0,
    "relevant_years": 0.0,
    "summary": "A 2-3 sentence professional summary highlighting key qualifications and fit for this role",
    "must_have_skills": ["skill1", "skill2", "skill3"],
    "nice_to_have_skills": ["skill1", "skill2", "skill3"],
    "experience_highlights": ["Most relevant experience point 1", "Most relevant experience point 2", "Most relevant experience point 3"],
    "strengths": ["Key strength 1", "Key strength 2", "Key strength 3"],
    "confidence_notes": "Brief assessment of candidate fit and any concerns or standout qualities"
}}

ANALYSIS GUIDELINES:
1. Extract the candidate's full name from the CV (usually at the top)
2. Focus on relevance to the specific job requirements
3. Extract years of experience accurately (total career vs relevant to this role)
4. Identify skills that directly match job requirements as "must_have_skills"
5. Include complementary skills as "nice_to_have_skills"
6. Highlight the most impressive and relevant experience points
7. Provide an honest assessment of candidate fit
8. Be concise but informative
9. Ensure all fields are properly filled

Return only the JSON object, no additional text.
"""
        
        print(f"🚀 Sending to OpenAI: {filename} (prompt: {len(prompt)} chars)")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        print(f"✅ OpenAI response received for {filename}: {len(content)} chars")
        
        # Clean JSON if wrapped in code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        try:
            analysis_data = json.loads(content)
            print(f"📊 JSON parsed successfully for {filename}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed for {filename}: {str(e)}")
            print(f"   Raw response: {content[:200]}...")
            return fallback_analysis(cv_text, filename, job_context)
        
        # Ensure all required fields with safe defaults
        result = CVAnalysis(
            source_file=filename,
            candidate_name=safe_get(analysis_data, 'candidate_name', 'Unknown Candidate'),
            current_title=safe_get(analysis_data, 'current_title', 'Not specified'),
            total_years=safe_float(analysis_data.get('total_years', 0)),
            relevant_years=safe_float(analysis_data.get('relevant_years', 0)),
            summary=safe_get(analysis_data, 'summary', 'No summary available'),
            must_have_skills=safe_list(analysis_data.get('must_have_skills', [])),
            nice_to_have_skills=safe_list(analysis_data.get('nice_to_have_skills', [])),
            experience_highlights=safe_list(analysis_data.get('experience_highlights', [])),
            strengths=safe_list(analysis_data.get('strengths', [])),
            confidence_notes=safe_get(analysis_data, 'confidence_notes', 'No assessment notes')
        )
        print(f"✅ Analysis completed for {filename} -> Candidate: {result.candidate_name}")
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error for {filename}: {str(e)}")
        logging.error(f"JSON parsing error for {filename}: {e}")
        return fallback_analysis(cv_text, filename, job_context)
    except Exception as e:
        print(f"❌ OpenAI analysis error for {filename}: {str(e)}")
        logging.error(f"OpenAI analysis error for {filename}: {e}")
        return fallback_analysis(cv_text, filename, job_context)

def fallback_analysis(cv_text: str, filename: str, job_context: Dict[str, Any]) -> CVAnalysis:
    """
    Fallback analysis when OpenAI is not available
    """
    print(f"⚠️  Using fallback analysis for: {filename} (CV text: {len(cv_text)} chars)")
    
    # Basic text analysis
    lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
    
    # Try to find a title (usually in first few lines)
    current_title = "Not specified"
    candidate_name = "Unknown Candidate"
    
    # Try to extract name from first few lines
    for line in lines[:5]:
        if len(line.split()) <= 4 and len(line) > 5 and not any(word in line.lower() for word in ['email', 'phone', 'address', '@']):
            candidate_name = line[:50]  # Limit length
            break
    
    for line in lines[:10]:
        if any(word in line.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'consultant', 'specialist']):
            current_title = line[:100]  # Limit length
            break
    
    # Rough year estimation (count year patterns)
    year_mentions = len([line for line in lines if any(str(year) in line for year in range(2000, 2025))])
    estimated_years = min(max(year_mentions * 1.2, 1), 15)  # Rough estimate
    
    # Basic skills extraction (look for common tech terms)
    common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes', 'git']
    found_skills = [skill for skill in common_skills if skill.lower() in cv_text.lower()]
    
    result = CVAnalysis(
        source_file=filename,
        candidate_name=candidate_name,
        current_title=current_title,
        total_years=float(estimated_years),
        relevant_years=float(estimated_years * 0.7),  # Assume 70% relevant
        summary=f"Candidate with approximately {estimated_years:.0f} years of experience. Basic analysis only - OpenAI required for detailed insights.",
        must_have_skills=found_skills[:5],
        nice_to_have_skills=found_skills[5:10] if len(found_skills) > 5 else [],
        experience_highlights=["Basic analysis only - full details require OpenAI"],
        strengths=["Analysis requires OpenAI API key"],
        confidence_notes="Limited analysis - please configure OpenAI API key for comprehensive evaluation"
    )
    print(f"✅ Fallback analysis completed for {filename} -> Candidate: {candidate_name}")
    return result

def safe_get(data: Dict, key: str, default: str = "") -> str:
    """Safely get string value from dict"""
    value = data.get(key, default)
    return str(value) if value is not None else default

def safe_float(value: Any) -> float:
    """Safely convert value to float"""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Extract numeric value from string
            numeric_chars = ''.join(c for c in value if c.isdigit() or c == '.')
            return float(numeric_chars) if numeric_chars else 0.0
        return 0.0
    except (ValueError, TypeError):
        return 0.0

def safe_list(value: Any) -> List[str]:
    """Safely convert value to list of strings"""
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    elif isinstance(value, dict):
        # If dict, extract values
        return [str(v) for v in value.values() if v is not None]
    elif isinstance(value, str):
        # If string, split by common delimiters
        return [item.strip() for item in value.split(',') if item.strip()]
    elif value is not None:
        return [str(value)]
    return []


def score_candidate_with_ai(candidate: CVAnalysis, job_title: str, job_description: str) -> tuple[float, str, str]:
    """
    Score candidate using AI analysis against job requirements
    Returns: (score 0-100, reasoning, brief_summary)
    """
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not openai_key:
        # Fallback to simple scoring if no API key
        base_score = min(95, max(20, candidate.total_years * 8 + candidate.relevant_years * 12))
        skill_bonus = len(candidate.must_have_skills) * 3 + len(candidate.nice_to_have_skills) * 1.5
        score = min(100, base_score + skill_bonus)
        brief_summary = f"{candidate.current_title} with {candidate.relevant_years}y relevant experience. Skills: {', '.join(candidate.must_have_skills[:3])}."
        return score, "Fallback scoring used (no API key available)", brief_summary
    
    try:
        client = OpenAI(api_key=openai_key)
        
        # Prepare candidate summary for scoring
        candidate_summary = f"""
Candidate: {candidate.candidate_name}
Current Title: {candidate.current_title}
Total Experience: {candidate.total_years} years
Relevant Experience: {candidate.relevant_years} years
Summary: {candidate.summary}
Key Skills: {', '.join(candidate.must_have_skills + candidate.nice_to_have_skills)}
Experience Highlights: {', '.join(candidate.experience_highlights)}
Strengths: {', '.join(candidate.strengths)}
"""
        
        scoring_prompt = f"""You are an expert recruiter evaluating candidates. Analyze this candidate against the job requirements and provide a comprehensive score.

JOB REQUIREMENTS:
Title: {job_title}
Description: {job_description}

CANDIDATE PROFILE:
{candidate_summary}

Evaluate the candidate on these criteria and provide a detailed scoring:

1. RELEVANT EXPERIENCE MATCH (40% weight)
   - How well does their experience align with job requirements?
   - Quality and depth of relevant experience
   - Career progression and growth

2. REQUIRED SKILLS COVERAGE (30% weight)
   - Coverage of must-have technical skills
   - Proficiency level indicators
   - Skill depth vs breadth

3. NICE-TO-HAVE SKILLS (15% weight)
   - Additional valuable skills mentioned
   - Bonus qualifications

4. EDUCATION & CERTIFICATIONS (10% weight)
   - Relevant educational background
   - Professional certifications
   - Continuous learning indicators

5. OVERALL FIT & POTENTIAL (5% weight)
   - Cultural fit indicators
   - Growth potential
   - Communication skills evident in CV

Provide a final score from 0-100 where:
- 90-100: Exceptional match, top candidate
- 80-89: Strong match, excellent candidate  
- 70-79: Good match, solid candidate
- 60-69: Moderate match, consider with reservations
- 50-59: Weak match, likely not suitable
- 0-49: Poor match, not recommended

Return your response in this exact JSON format:
{{
    "score": 85,
    "reasoning": "Strong candidate with 8+ years relevant experience in Python development. Excellent match for senior role requirements including microservices, AWS, and team leadership. Missing some nice-to-have skills like Kubernetes but overall very well-qualified.",
    "brief_summary": "Senior Python Developer with 8y experience, strong in microservices & AWS, excellent team leadership skills",
    "experience_match": 88,
    "skills_coverage": 82,
    "nice_to_have": 70,
    "education": 85,
    "overall_fit": 90
}}

The brief_summary should be 1-2 sentences maximum, highlighting the candidate's current role, key experience, and standout skills relevant to this position."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert recruiter with deep knowledge of technical roles and candidate evaluation. Provide honest, detailed, and consistent scoring."
                },
                {
                    "role": "user",
                    "content": scoring_prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content
        
        try:
            result = json.loads(result_text)
            score = float(result.get('score', 0))
            reasoning = result.get('reasoning', 'No reasoning provided')
            brief_summary = result.get('brief_summary', f"{candidate.current_title} with {candidate.relevant_years}y experience")
            
            # Ensure score is within valid range
            score = max(0, min(100, score))
            
            return score, reasoning, brief_summary
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            print(f"Failed to parse AI scoring response: {result_text}")
            fallback_score = min(95, max(20, candidate.total_years * 8 + candidate.relevant_years * 12))
            skill_bonus = len(candidate.must_have_skills) * 3 + len(candidate.nice_to_have_skills) * 1.5
            score = min(100, fallback_score + skill_bonus)
            brief_summary = f"{candidate.current_title} with {candidate.relevant_years}y relevant experience"
            return score, "AI scoring failed, used fallback calculation", brief_summary
            
    except Exception as e:
        print(f"Error in AI scoring: {str(e)}")
        # Fallback to simple scoring
        base_score = min(95, max(20, candidate.total_years * 8 + candidate.relevant_years * 12))
        skill_bonus = len(candidate.must_have_skills) * 3 + len(candidate.nice_to_have_skills) * 1.5
        score = min(100, base_score + skill_bonus)
        brief_summary = f"{candidate.current_title} with {candidate.relevant_years}y relevant experience"
        return score, f"AI scoring error, used fallback: {str(e)}", brief_summary
