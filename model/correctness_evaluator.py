#!/usr/bin/env python3
"""
Content Correctness Evaluator
Uses fact_check_agent to assess the factual accuracy of lecture content against source materials.
"""

import json
import asyncio
import openai
import os
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client for v1.x API
OPENAI_AVAILABLE = bool(os.getenv('OPENAI_API_KEY'))
if OPENAI_AVAILABLE:
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("✅ OpenAI API configured for fact checking")
else:
    client = None
    print("⚠️ OpenAI API key not found - fact checking will use fallback methods")

# Try to import fact checking agent
FACT_CHECK_AGENT_AVAILABLE = False
try:
    from .fact_check_agent_custom import fact_check_agent, Runner
    FACT_CHECK_AGENT_AVAILABLE = True
    print("✅ Custom fact check agent loaded successfully")
except ImportError as e:
    print(f"⚠️ Custom fact check agent not available: {e}")
    FACT_CHECK_AGENT_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Custom fact check agent failed to load: {e}")
    FACT_CHECK_AGENT_AVAILABLE = False

# Debug function to check what's available
def debug_fact_check_status():
    """Debug function to check fact checking capabilities"""
    print(f"🔍 DEBUG: FACT_CHECK_AGENT_AVAILABLE = {FACT_CHECK_AGENT_AVAILABLE}")
    print(f"🔍 DEBUG: OPENAI_AVAILABLE = {OPENAI_AVAILABLE}")
    return FACT_CHECK_AGENT_AVAILABLE, OPENAI_AVAILABLE


async def analyze_content_correctness_with_agent(transcript_text: str, source_materials: str) -> Tuple[float, Dict[str, Any]]:
    """
    Use fact_check_agent to analyze content correctness
    
    Args:
        transcript_text: The lecture transcript
        source_materials: Reference materials for fact checking
        
    Returns:
        Tuple of (correctness_score, analysis_details)
    """
    if not FACT_CHECK_AGENT_AVAILABLE:
        raise ImportError("Fact check agent not available")
    
    if not source_materials.strip():
        raise ValueError("No source materials provided for fact checking")
    
    try:
        print(f"🔄 Starting fact check agent with {len(source_materials)} chars of source material")
        
        # Prepare prompt for fact checking agent
        prompt = f"""TRANSCRIPT:
{transcript_text}

SOURCE MATERIALS:
{source_materials}

Please analyze the transcript against the source materials and provide your assessment in the required JSON format."""
        
        # Run the fact checking agent
        print("🔄 Running fact check agent...")
        result = await Runner.run(fact_check_agent, prompt)
        raw_output = result.final_output
        print(f"✅ Fact check agent completed, got {len(raw_output)} chars of output")
        
        # Parse the JSON response from the fact checking agent
        try:
            fact_check_data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON (error at char {e.pos}), trying regex extraction...")
            # Try to extract JSON from the response if it's wrapped in text
            import re
            
            # Try multiple extraction patterns
            patterns = [
                r'\{.*\}',  # Basic JSON object
                r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                r'```\s*(\{.*?\})\s*```',  # JSON in code blocks without language
            ]
            
            fact_check_data = None
            for pattern in patterns:
                json_match = re.search(pattern, raw_output, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group()
                        fact_check_data = json.loads(json_str)
                        print("✅ Successfully extracted JSON using regex")
                        break
                    except json.JSONDecodeError:
                        continue
            
            if fact_check_data is None:
                print(f"❌ Could not extract valid JSON from response:")
                print(f"First 500 chars: {raw_output[:500]}...")
                print(f"Last 500 chars: ...{raw_output[-500:]}")
                # Return a fallback structure
                fact_check_data = {
                    "summary": {"overall_judgment": "mixed", "notes": "Failed to parse fact check response"},
                    "claims": [],
                    "digressions": []
                }
        
        # Calculate correctness score based on analysis
        claims = fact_check_data.get('claims', [])
        if not claims:
            return 0.7, {**fact_check_data, 'method': 'fact_check_agent'}  # Default score if no claims found
        
        correct_count = len([c for c in claims if c.get('judgment') == 'Correct'])
        incorrect_count = len([c for c in claims if c.get('judgment') == 'Incorrect'])
        unsupported_count = len([c for c in claims if c.get('judgment') == 'Unsupported'])
        
        total_claims = len(claims)
        
        # More forgiving scoring: Correct = 1.0, Unsupported = 0.7, Incorrect = 0.2
        # This reduces the impact of unsupported claims and gives some benefit of doubt for "incorrect" claims
        correctness_ratio = (correct_count * 1.0 + unsupported_count * 0.7 + incorrect_count * 0.2) / total_claims
        
        # Check for digressions and apply penalty
        digressions = fact_check_data.get('digressions', [])
        digression_penalty = 0
        for digression in digressions:
            severity = digression.get('severity', 'Low')
            if severity == 'High':
                digression_penalty += 0.05  # Reduced penalty
            elif severity == 'Medium':
                digression_penalty += 0.03  # Reduced penalty
            else:  # Low
                digression_penalty += 0.01  # Reduced penalty
        
        final_score = max(0.1, correctness_ratio - digression_penalty)  # Minimum score of 0.1
        
        # Add scoring details to analysis
        fact_check_data.update({
            'method': 'fact_check_agent',
            'scoring_details': {
                'correct_claims': correct_count,
                'incorrect_claims': incorrect_count,
                'unsupported_claims': unsupported_count,
                'total_claims': total_claims,
                'correctness_ratio': correctness_ratio,
                'digression_penalty': digression_penalty,
                'final_score': final_score,
                'digressions_count': len(digressions)
            }
        })
        
        print(f"✅ Fact check agent analysis complete: {final_score:.2f} score")
        return final_score, fact_check_data
        
    except Exception as e:
        print(f"❌ Fact check agent analysis error: {e}")
        # Return moderate correctness as fallback
        return 0.6, {"error": str(e), "method": "fact_check_agent_fallback"}


def analyze_content_correctness_with_openai(transcript_text: str, source_materials: str) -> Tuple[float, Dict[str, Any]]:
    """
    Use OpenAI directly to analyze content correctness (fallback when agent unavailable)
    
    Args:
        transcript_text: The lecture transcript
        source_materials: Reference materials for fact checking
        
    Returns:
        Tuple of (correctness_score, analysis_details)
    """
    if not OPENAI_AVAILABLE or not source_materials.strip():
        raise ImportError("OpenAI API not available or no source materials provided")
    
    # Prepare prompt for fact checking
    fact_check_prompt = f"""You are an expert fact-checker. Compare this lecture transcript against the provided source materials.

TRANSCRIPT:
{transcript_text}

SOURCE MATERIALS:
{source_materials}

Analyze the transcript and return a JSON assessment with this exact schema:
{{
  "summary": {{
    "overall_judgment": "mostly_correct | mixed | mostly_incorrect",
    "notes": "short summary of findings"
  }},
  "claims": [
    {{
      "claim": "string",
      "judgment": "Correct | Incorrect | Unsupported",
      "evidence": "quote or section from source text (if applicable)",
      "explanation": "brief reasoning"
    }}
  ],
  "digressions": [
    {{
      "snippet": "transcript excerpt",
      "why_digression": "reason it's off-topic",
      "severity": "Low | Medium | High"
    }}
  ]
}}

Focus on extracting key factual claims and judging them as:
- Correct: supported by the source text
- Incorrect: contradicted by the source text  
- Unsupported: not verifiable from the source text

Return only valid JSON."""
    
    try:
        # Use OpenAI API v1.x syntax
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": fact_check_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content
        fact_check_data = json.loads(result_text)
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to simple analysis
        return analyze_content_correctness_fallback(transcript_text, source_materials)
    
    # Calculate correctness score based on analysis
    claims = fact_check_data.get('claims', [])
    if not claims:
        return 0.7, fact_check_data  # Default score if no claims found
    
    correct_count = len([c for c in claims if c.get('judgment') == 'Correct'])
    incorrect_count = len([c for c in claims if c.get('judgment') == 'Incorrect'])
    unsupported_count = len([c for c in claims if c.get('judgment') == 'Unsupported'])
    
    total_claims = len(claims)
    
    # Scoring: Correct = 1.0, Unsupported = 0.5, Incorrect = 0.0
    correctness_ratio = (correct_count + 0.5 * unsupported_count) / total_claims
    
    # Check for digressions
    digressions = fact_check_data.get('digressions', [])
    digression_penalty = len(digressions) * 0.05  # 5% penalty per digression
    
    final_score = max(0.0, correctness_ratio - digression_penalty)
    
    # Add scoring details to analysis
    fact_check_data.update({
        'method': 'openai_enhanced',
        'scoring_details': {
            'correct_claims': correct_count,
            'incorrect_claims': incorrect_count,
            'unsupported_claims': unsupported_count,
            'total_claims': total_claims,
            'correctness_ratio': correctness_ratio,
            'digression_penalty': digression_penalty,
            'final_score': final_score
        }
    })
    
    return final_score, fact_check_data


def analyze_content_correctness_fallback(transcript_text: str, source_materials: str) -> Tuple[float, Dict[str, Any]]:
    """
    Fallback correctness analysis without AI agents
    
    Args:
        transcript_text: The lecture transcript
        source_materials: Reference materials for comparison
        
    Returns:
        Tuple of (correctness_score, analysis_details)
    """
    if not source_materials.strip():
        return 0.6, {"note": "No source materials for comparison", "method": "fallback"}
    
    # Simple keyword overlap analysis
    transcript_words = set(transcript_text.lower().split())
    source_words = set(source_materials.lower().split())
    
    overlap = len(transcript_words.intersection(source_words))
    total_unique = len(transcript_words.union(source_words))
    
    similarity_ratio = overlap / total_unique if total_unique > 0 else 0
    
    analysis_details = {
        "method": "keyword_overlap_fallback",
        "similarity_ratio": similarity_ratio,
        "transcript_words": len(transcript_words),
        "source_words": len(source_words),
        "overlapping_words": overlap
    }
    
    return similarity_ratio, analysis_details


async def calculate_correctness_score(transcript_text: str, source_materials: str, duration: Optional[int] = None) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate content correctness score (40% of total evaluation)
    
    Args:
        transcript_text: The lecture transcript
        source_materials: Reference materials for fact checking
        duration: Lecture duration in minutes (for fallback scoring)
        
    Returns:
        Tuple of (score_out_of_40, analysis_details)
    """
    # Debug what we have available
    print(f"🔍 DEBUG: Starting correctness evaluation")
    print(f"🔍 DEBUG: FACT_CHECK_AGENT_AVAILABLE = {FACT_CHECK_AGENT_AVAILABLE}")
    print(f"🔍 DEBUG: OPENAI_AVAILABLE = {OPENAI_AVAILABLE}")
    print(f"🔍 DEBUG: Source materials length = {len(source_materials)} chars")
    print(f"🔍 DEBUG: Source materials content preview: {source_materials[:200]}...")
    
    try:
        # Try using the fact check agent first (preferred method)
        if FACT_CHECK_AGENT_AVAILABLE and source_materials.strip():
            print("🔄 Attempting fact check agent analysis...")
            try:
                correctness_ratio, analysis_details = await analyze_content_correctness_with_agent(
                    transcript_text, source_materials
                )
                print("✅ Fact check agent analysis complete")
                
                # Apply bonus for having source materials
                if source_materials.strip():
                    material_bonus = min(len(source_materials.split()) / 1000, 0.1)  # Up to 10% bonus
                    correctness_ratio = min(correctness_ratio + material_bonus, 1.0)
                    analysis_details['material_bonus'] = material_bonus
                
                correctness_score = correctness_ratio * 40
                analysis_details['final_score_out_of_40'] = correctness_score
                
                return correctness_score, analysis_details
                
            except Exception as agent_error:
                print(f"❌ Fact check agent failed: {agent_error}")
                # Fall through to OpenAI backup
        else:
            print(f"⚠️ Fact check agent not available. Agent: {FACT_CHECK_AGENT_AVAILABLE}, Materials: {bool(source_materials.strip())}")
            
        # Fall back to OpenAI direct if agent not available
        if OPENAI_AVAILABLE and source_materials.strip():
            print("🔄 Falling back to OpenAI direct fact checking...")
            # Run in thread since OpenAI v1.x is sync
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    analyze_content_correctness_with_openai,
                    transcript_text, source_materials
                )
                correctness_ratio, analysis_details = future.result(timeout=30)
            print("✅ OpenAI fact checking complete")
            
        # Ultimate fallback to keyword analysis
        else:
            print("⚠️ No AI available, using keyword fallback...")
            correctness_ratio, analysis_details = analyze_content_correctness_fallback(
                transcript_text, source_materials
            )
            
        # Apply bonus for having source materials
        if source_materials.strip():
            material_bonus = min(len(source_materials.split()) / 1000, 0.1)  # Up to 10% bonus
            correctness_ratio = min(correctness_ratio + material_bonus, 1.0)
            analysis_details['material_bonus'] = material_bonus
        
        correctness_score = correctness_ratio * 40
        analysis_details['final_score_out_of_40'] = correctness_score
        
        return correctness_score, analysis_details
        
    except Exception as e:
        print(f"❌ Error in correctness calculation: {e}")
        # Ultimate fallback - basic content density
        word_count = len(transcript_text.split())
        content_density = min(word_count / (duration * 10), 1.0) if duration else 0.5
        correctness_score = content_density * 40
        
        analysis_details = {
            "method": "basic_density_fallback",
            "content_density": content_density,
            "word_count": word_count,
            "error": str(e),
            "final_score_out_of_40": correctness_score
        }
        
        return correctness_score, analysis_details