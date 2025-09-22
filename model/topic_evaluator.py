#!/usr/bin/env python3
"""
Topic Coverage Evaluator
Analyzes how well the lecture covers the intended topics.
"""

from typing import Dict, Any, Tuple, List
import re
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client for v1.x API
OPENAI_AVAILABLE = bool(os.getenv('OPENAI_API_KEY'))
if OPENAI_AVAILABLE:
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("✅ OpenAI API configured for topic analysis")
else:
    client = None
    print("⚠️ OpenAI API key not found - topic analysis will use fallback methods")


def analyze_topic_coverage_with_openai(topics_list: List[str], combined_content: str) -> Dict[str, Any]:
    """
    Use OpenAI to intelligently analyze topic coverage and depth
    
    Args:
        topics_list: List of expected topics to analyze
        combined_content: Combined text content from transcript, materials, and slides
        
    Returns:
        Dictionary with detailed topic analysis including coverage scores and explanations
    """
    if not OPENAI_AVAILABLE or not topics_list:
        raise ImportError("OpenAI API not available or no topics provided")
    
    topics_str = ", ".join(topics_list)
    
    # Prepare prompt for topic analysis
    topic_analysis_prompt = f"""You are an expert educational content analyst. Analyze how well this lecture content covers the specified topics.

EXPECTED TOPICS: {topics_str}

LECTURE CONTENT:
{combined_content}

Analyze the content and return a JSON assessment with this exact schema:
{{
  "overall_analysis": {{
    "coverage_score": 0.0,
    "depth_score": 0.0,
    "summary": "Brief overall assessment"
  }},
  "topic_analysis": [
    {{
      "topic": "topic name",
      "coverage_status": "well_covered | partially_covered | mentioned | not_covered",
      "coverage_score": 0.0,
      "depth_score": 0.0,
      "evidence": ["relevant quotes or sections from content"],
      "explanation": "detailed analysis of how well this topic is covered",
      "suggestions": "recommendations for improvement"
    }}
  ],
  "additional_insights": {{
    "well_structured": true,
    "coherent_flow": true,
    "appropriate_depth": true,
    "missing_connections": ["topics that should be connected but aren't"],
    "unexpected_topics": ["topics covered but not in expected list"]
  }}
}}

Scoring Guidelines:
- coverage_score: 0.0-1.0 based on how much of the topic is addressed
- depth_score: 0.0-1.0 based on how thoroughly the topic is explained
- overall scores should be averages of individual topic scores

Focus on:
1. Whether each topic is actually discussed
2. How thoroughly each topic is explained
3. Quality of examples and explanations
4. Logical flow between topics
5. Appropriate depth for the educational level

Return only valid JSON."""
    
    try:
        # Use OpenAI API v1.x syntax
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": topic_analysis_prompt}
            ],
            temperature=0.1,
            max_tokens=3000
        )
        
        result_text = response.choices[0].message.content
        topic_analysis_data = json.loads(result_text)
        
        # Add method identifier
        topic_analysis_data['analysis_method'] = 'openai_enhanced'
        
        return topic_analysis_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in OpenAI response: {e}")
        # Fallback to simple analysis
        return analyze_topic_coverage_fallback(topics_list, combined_content)
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to simple analysis
        return analyze_topic_coverage_fallback(topics_list, combined_content)


def analyze_topic_coverage_fallback(topics_list: List[str], combined_content: str) -> Dict[str, Any]:
    """
    Fallback topic analysis using the original string matching approach
    
    Args:
        topics_list: List of expected topics
        combined_content: Combined text content
        
    Returns:
        Dictionary with basic topic analysis
    """
    coverage_analysis = analyze_topic_coverage(topics_list, combined_content)
    depth_analysis = analyze_topic_depth(topics_list, combined_content)
    
    # Convert to OpenAI-like format
    topic_analysis = []
    for i, topic in enumerate(topics_list):
        is_covered = any(ct['topic'] == topic for ct in coverage_analysis['covered_topics'])
        
        if is_covered:
            depth_info = next((d for d in depth_analysis['depth_scores'] if d['topic'] == topic), {})
            coverage_score = 0.8  # High score for covered topics
            depth_score = min(depth_info.get('depth_score', 0) / 5.0, 1.0)  # Normalize to 0-1
            status = "well_covered" if depth_score > 0.6 else "partially_covered"
        else:
            coverage_score = 0.0
            depth_score = 0.0
            status = "not_covered"
        
        topic_analysis.append({
            "topic": topic,
            "coverage_status": status,
            "coverage_score": coverage_score,
            "depth_score": depth_score,
            "evidence": [],
            "explanation": f"Topic '{topic}' analysis using fallback method",
            "suggestions": "Use OpenAI analysis for detailed insights"
        })
    
    overall_coverage = sum(ta['coverage_score'] for ta in topic_analysis) / len(topic_analysis) if topic_analysis else 0
    overall_depth = sum(ta['depth_score'] for ta in topic_analysis) / len(topic_analysis) if topic_analysis else 0
    
    return {
        "overall_analysis": {
            "coverage_score": overall_coverage,
            "depth_score": overall_depth,
            "summary": "Fallback analysis - limited insights available"
        },
        "topic_analysis": topic_analysis,
        "additional_insights": {
            "well_structured": True,
            "coherent_flow": True,
            "appropriate_depth": True,
            "missing_connections": [],
            "unexpected_topics": []
        },
        "analysis_method": "fallback"
    }


def extract_topics_from_text(topics_covered: str) -> List[str]:
    """
    Extract and clean topic list from input string
    
    Args:
        topics_covered: Comma-separated topics string
        
    Returns:
        List of cleaned topic strings
    """
    if not topics_covered or not topics_covered.strip():
        return []
    
    topics = [topic.strip() for topic in topics_covered.split(",")]
    return [topic for topic in topics if topic]  # Remove empty strings


def analyze_topic_coverage(topics_list: List[str], combined_content: str) -> Dict[str, Any]:
    """
    Analyze how well topics are covered in the content
    
    Args:
        topics_list: List of expected topics
        combined_content: Combined text content to search
        
    Returns:
        Dictionary with coverage analysis
    """
    if not topics_list:
        return {
            'covered_topics': [],
            'uncovered_topics': [],
            'coverage_ratio': 0,
            'total_topics': 0
        }
    
    content_lower = combined_content.lower()
    covered_topics = []
    uncovered_topics = []
    
    for topic in topics_list:
        topic_lower = topic.lower()
        
        # Check for exact match
        if topic_lower in content_lower:
            covered_topics.append({
                'topic': topic,
                'match_type': 'exact',
                'occurrences': content_lower.count(topic_lower)
            })
        else:
            # Check for partial matches (individual words from topic)
            topic_words = topic_lower.split()
            if len(topic_words) > 1:
                word_matches = sum(1 for word in topic_words if word in content_lower)
                if word_matches >= len(topic_words) * 0.5:  # At least 50% of words match
                    covered_topics.append({
                        'topic': topic,
                        'match_type': 'partial',
                        'word_matches': word_matches,
                        'total_words': len(topic_words)
                    })
                else:
                    uncovered_topics.append(topic)
            else:
                uncovered_topics.append(topic)
    
    coverage_ratio = len(covered_topics) / len(topics_list) if topics_list else 0
    
    return {
        'covered_topics': covered_topics,
        'uncovered_topics': uncovered_topics,
        'coverage_ratio': coverage_ratio,
        'total_topics': len(topics_list)
    }


def analyze_topic_depth(topics_list: List[str], combined_content: str) -> Dict[str, Any]:
    """
    Analyze the depth of topic coverage
    
    Args:
        topics_list: List of expected topics
        combined_content: Combined text content to analyze
        
    Returns:
        Dictionary with depth analysis
    """
    if not topics_list:
        return {'depth_scores': [], 'average_depth': 0}
    
    content_lower = combined_content.lower()
    depth_scores = []
    
    for topic in topics_list:
        topic_lower = topic.lower()
        
        # Count occurrences and surrounding context
        occurrences = content_lower.count(topic_lower)
        
        if occurrences > 0:
            # Find contexts around the topic mentions
            contexts = []
            start_pos = 0
            while True:
                pos = content_lower.find(topic_lower, start_pos)
                if pos == -1:
                    break
                
                # Extract context (50 words before and after)
                words = combined_content.split()
                word_pos = len(combined_content[:pos].split())
                context_start = max(0, word_pos - 25)
                context_end = min(len(words), word_pos + 25)
                context = ' '.join(words[context_start:context_end])
                contexts.append(context)
                
                start_pos = pos + len(topic_lower)
            
            # Calculate depth score based on occurrences and context length
            avg_context_length = sum(len(ctx.split()) for ctx in contexts) / len(contexts)
            depth_score = min(occurrences * 0.3 + avg_context_length * 0.02, 5.0)  # Max 5.0
            
            depth_scores.append({
                'topic': topic,
                'occurrences': occurrences,
                'avg_context_length': avg_context_length,
                'depth_score': depth_score
            })
        else:
            depth_scores.append({
                'topic': topic,
                'occurrences': 0,
                'avg_context_length': 0,
                'depth_score': 0
            })
    
    average_depth = sum(d['depth_score'] for d in depth_scores) / len(depth_scores) if depth_scores else 0
    
    return {
        'depth_scores': depth_scores,
        'average_depth': average_depth
    }


def calculate_topic_coverage_score(topics_covered: str, combined_content: str) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate topic coverage score using OpenAI for intelligent analysis
    
    Args:
        topics_covered: Comma-separated string of expected topics
        combined_content: Combined text from transcript, materials, and slides
        
    Returns:
        Tuple of (score_out_of_10, analysis_details)
    """
    # Extract topics list
    topics_list = extract_topics_from_text(topics_covered)
    
    if not topics_list:
        return 5.0, {  # Default score if no topics specified
            'message': 'No topics specified for evaluation',
            'final_score_out_of_10': 5.0,
            'analysis_method': 'no_topics'
        }
    
    try:
        # Try OpenAI analysis first
        if OPENAI_AVAILABLE:
            analysis_result = analyze_topic_coverage_with_openai(topics_list, combined_content)
            
            # Extract scores from OpenAI analysis
            overall_analysis = analysis_result.get('overall_analysis', {})
            coverage_score = overall_analysis.get('coverage_score', 0.0)
            depth_score = overall_analysis.get('depth_score', 0.0)
            
            # Calculate final score (out of 10)
            # 70% weight on coverage, 30% weight on depth
            final_score = min((coverage_score * 7.0) + (depth_score * 3.0), 10.0)
            
            analysis_result.update({
                'scoring_details': {
                    'coverage_score': coverage_score,
                    'depth_score': depth_score,
                    'coverage_weight': 0.7,
                    'depth_weight': 0.3,
                    'final_score_out_of_10': final_score
                },
                'final_score_out_of_10': final_score
            })
            
            return final_score, analysis_result
            
    except Exception as e:
        print(f"OpenAI analysis failed, using fallback: {e}")
    
    # Fallback to original analysis method
    try:
        fallback_analysis = analyze_topic_coverage_fallback(topics_list, combined_content)
        
        overall_analysis = fallback_analysis.get('overall_analysis', {})
        coverage_score = overall_analysis.get('coverage_score', 0.0)
        depth_score = overall_analysis.get('depth_score', 0.0)
        
        # Calculate final score (out of 10)
        final_score = min((coverage_score * 7.0) + (depth_score * 3.0), 10.0)
        
        fallback_analysis.update({
            'scoring_details': {
                'coverage_score': coverage_score,
                'depth_score': depth_score,
                'coverage_weight': 0.7,
                'depth_weight': 0.3,
                'final_score_out_of_10': final_score
            },
            'final_score_out_of_10': final_score
        })
        
        return final_score, fallback_analysis
        
    except Exception as e:
        print(f"Fallback analysis also failed: {e}")
        
        # Final fallback - use original method
        coverage_analysis = analyze_topic_coverage(topics_list, combined_content)
        depth_analysis = analyze_topic_depth(topics_list, combined_content)
        
        # Calculate base score from coverage ratio
        base_score = coverage_analysis['coverage_ratio'] * 7  # Up to 7 points for coverage
        
        # Add depth bonus
        depth_bonus = min(depth_analysis['average_depth'] * 0.6, 3)  # Up to 3 points for depth
        
        # Calculate final score
        total_score = min(base_score + depth_bonus, 10)  # Max 10 points
        
        analysis_details = {
            'topics_analysis': coverage_analysis,
            'depth_analysis': depth_analysis,
            'base_score': base_score,
            'depth_bonus': depth_bonus,
            'final_score_out_of_10': total_score,
            'analysis_method': 'original_fallback'
        }
        
        return total_score, analysis_details