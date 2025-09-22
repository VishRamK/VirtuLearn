#!/usr/bin/env python3
"""
Main Lecture Evaluator
Orchestrates all evaluation components and provides the main scoring interface.
"""

import asyncio
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from .correctness_evaluator import calculate_correctness_score
from .engagement_evaluator import calculate_engagement_score, calculate_engagement_score_sync
from .topic_evaluator import calculate_topic_coverage_score


async def calculate_comprehensive_lecture_score(
    transcript_text: str,
    topics_covered: str,
    duration: Optional[int] = None,
    source_materials: str = "",
    slides_content: str = ""
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Calculate comprehensive lecture quality score using all evaluation components
    
    Args:
        transcript_text: The lecture transcript
        topics_covered: Comma-separated expected topics
        duration: Lecture duration in minutes
        source_materials: Reference materials for fact checking
        slides_content: Text content from presentation slides
        
    Returns:
        Tuple of (total_score, score_components, detailed_analysis)
    """
    score_components = {}
    detailed_analysis = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'evaluation_method': 'comprehensive_ai_analysis'
    }
    
    # Combine all content for comprehensive analysis
    combined_content = transcript_text
    if source_materials:
        combined_content += "\n\n--- SOURCE MATERIALS ---\n" + source_materials
    if slides_content:
        combined_content += "\n\n--- SLIDES CONTENT ---\n" + slides_content
    
    try:
        # 1. Correctness (30 points max)
        correctness_score, correctness_details = await calculate_correctness_score(
            transcript_text, source_materials, duration
        )
        # Scale to 40 points max
        score_components['Correctness'] = min(correctness_score * 0.75, 40)  # 40 * 0.75 = 30
        detailed_analysis['correctness'] = correctness_details
        
        # 2. Engagement (30 points max)  
        engagement_score, engagement_details = await calculate_engagement_score(
            transcript_text, slides_content
        )
        # Scale to 30 points max
        score_components['Engagement'] = min(engagement_score * 0.571, 30)  # 35 * 0.571 = 30
        detailed_analysis['engagement'] = engagement_details

        # 3. Topic Coverage (30 points max)
        topic_score, topic_details = calculate_topic_coverage_score(
            topics_covered, combined_content
        )
        # Scale to 30 points max
        score_components['Topic Coverage'] = min(topic_score * 3.0, 30)  # 10 * 3.0 = 30
        detailed_analysis['topic_coverage'] = topic_details

        # Calculate total score
        total_score = sum(score_components.values())
        detailed_analysis['total_score'] = total_score
        detailed_analysis['score_components'] = score_components
        
        return total_score, score_components, detailed_analysis
        
    except Exception as e:
        # If async operations fail, provide fallback scores
        detailed_analysis['error'] = str(e)
        detailed_analysis['evaluation_method'] = 'fallback_analysis'
        
        # Basic fallback scoring
        word_count = len(transcript_text.split())
        
        # Basic fallback scoring with corrected weights
        score_components['Correctness'] = min(word_count / 200, 30)  # Scale to 30 max
        score_components['Engagement'] = min(transcript_text.count('?') * 2.5, 20)  # Scale to 20 max
        score_components['Topic Coverage'] = 20  # Default moderate score out of 30
        
        total_score = sum(score_components.values())
        detailed_analysis['total_score'] = total_score
        detailed_analysis['score_components'] = score_components
        
        return total_score, score_components, detailed_analysis


def generate_comprehensive_evaluation_report(
    score: float,
    score_components: Dict[str, float],
    transcript_text: str,
    topics_covered: str,
    analysis_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed evaluation report with AI analysis insights
    
    Args:
        score: Total evaluation score
        score_components: Breakdown of scores by component
        transcript_text: The lecture transcript
        topics_covered: Expected topics
        analysis_details: Detailed analysis from evaluation components
        
    Returns:
        Comprehensive evaluation report dictionary
    """
    report = {
        'overall_score': score,
        'grade': 'A' if score >= 85 else 'B' if score >= 75 else 'C' if score >= 65 else 'D' if score >= 55 else 'F',
        'score_breakdown': score_components,
        'word_count': len(transcript_text.split()),
        'topics_covered': [topic.strip() for topic in topics_covered.split(",")] if topics_covered else [],
        'timestamp': datetime.now().isoformat(),
        'analysis_details': analysis_details
    }
    
    # Generate AI-enhanced recommendations
    recommendations = []
    
    # Generate AI-enhanced recommendations with specific evidence
    recommendations = []
    
    # Generate specific recommendations with transcript evidence
    if analysis_details.get('correctness'):
        correctness = analysis_details['correctness']
        
        # Fact-checking recommendations with evidence
        if 'agent_analysis' in correctness:
            agent_analysis = correctness['agent_analysis']
            full_analysis = agent_analysis.get('full_analysis', {})
            fact_checks = full_analysis.get('fact_checks', [])
            
            # Find specific incorrect claims
            incorrect_claims = [fc for fc in fact_checks if fc.get('verdict') in ['INCORRECT', 'QUESTIONABLE']]
            if incorrect_claims:
                for claim in incorrect_claims[:2]:  # Show top 2 issues
                    claim_text = claim.get('claim', 'Unknown claim')[:100] + "..."
                    recommendations.append(f"⚠️ Factual concern: '{claim_text}' - {claim.get('explanation', 'Verify accuracy')}")
            
            # Check for unsupported claims
            unsupported = [fc for fc in fact_checks if fc.get('verdict') == 'UNSUPPORTED']
            if len(unsupported) > 2:
                recommendations.append(f"📚 {len(unsupported)} claims need supporting evidence - cite sources for factual statements")
        
        elif correctness.get('method') == 'fallback_keyword_overlap':
            similarity = correctness.get('correctness_ratio', 0)
            if similarity < 0.3:
                recommendations.append("📚 Low alignment with source materials - incorporate more reference content")
    
    if analysis_details.get('engagement'):
        engagement = analysis_details['engagement']
        
        # AI-driven engagement recommendations with specific evidence
        if 'agent_analysis' in engagement:
            agent_analysis = engagement['agent_analysis']
            full_analysis = agent_analysis.get('full_analysis', {})
            quantitative = full_analysis.get('quantitative_metrics', {})
            
            # Student talk ratio analysis
            student_talk_ratio = quantitative.get('student_talk_ratio', 0)
            if student_talk_ratio < 10:
                recommendations.append(f"�️ Very low student participation ({student_talk_ratio:.1f}%) - encourage more questions and discussion")
            elif student_talk_ratio > 25:
                recommendations.append(f"⚖️ High student talk ratio ({student_talk_ratio:.1f}%) - ensure adequate content coverage")
            
            # Turn frequency analysis
            turns_per_10min = quantitative.get('turns_per_10min', 0)
            if turns_per_10min < 2:
                recommendations.append("� Few interaction opportunities - add polls, questions, or discussion breaks")
            
            # Question analysis
            qualitative = full_analysis.get('qualitative_analysis', {})
            question_types = qualitative.get('question_distribution', {})
            if question_types:
                total_questions = sum(question_types.values())
                if total_questions < 3:
                    recommendations.append("❓ Limited questioning - incorporate more interactive elements")
        
        elif 'reconstructed_questions' in engagement:
            recon_q = engagement['reconstructed_questions']
            if recon_q > 0:
                recommendations.append(f"💡 {recon_q} potential student questions identified - encourage more interaction")

    if analysis_details.get('topic_coverage'):
        topic_coverage = analysis_details['topic_coverage']

        # Topic coverage recommendations with specifics
        if 'topics_analysis' in topic_coverage:
            topics_analysis = topic_coverage['topics_analysis']
            uncovered = topics_analysis.get('uncovered_topics', [])
            if uncovered:
                recommendations.append(f"📝 Address missing topics: {', '.join(uncovered[:3])}")
            
            # Depth analysis
            depth_analysis = topic_coverage.get('depth_analysis', {})
            avg_depth = depth_analysis.get('average_depth', 0)
            if avg_depth < 2.0:
                shallow_topics = [t for t, d in depth_analysis.get('topic_depths', {}).items() if d < 2.0]
                if shallow_topics:
                    recommendations.append(f"🔬 Provide deeper coverage of: {', '.join(shallow_topics[:2])}")
    
    # Overall performance recommendations
    if score >= 85:
        recommendations.append("🌟 Excellent lecture! Consider sharing best practices with colleagues")
    # Overall performance recommendations
    if score >= 85:
        recommendations.append("🌟 Excellent lecture! Consider sharing best practices with colleagues")
    elif score >= 70:
        recommendations.append("👍 Good lecture with room for focused improvements")
    else:
        recommendations.append("⚠️ Significant improvements needed - consider peer observation or additional training")
    
    report['recommendations'] = recommendations
    
    return report


def run_evaluation_sync(
    transcript_text: str,
    topics_covered: str,
    duration: Optional[int] = None,
    source_materials: str = "",
    slides_content: str = ""
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Synchronous wrapper for evaluation (for Streamlit compatibility)
    This version attempts async evaluation with proper error handling
    """
    
    try:
        # Try to run async evaluation in a thread-safe way
        import threading
        import concurrent.futures
        
        def run_async_eval():
            """Run async evaluation in a separate thread"""
            try:
                # Create new event loop in this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        calculate_comprehensive_lecture_score(
                            transcript_text, topics_covered, duration, source_materials, slides_content
                        )
                    )
                finally:
                    loop.close()
            except Exception as e:
                print(f"🔄 Async evaluation failed: {e}")
                return None
        
        # Run in thread to avoid event loop conflicts
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_async_eval)
            result = future.result(timeout=60)  # 60 second timeout
            
            if result is not None:
                print("✅ Async evaluation completed successfully")
                return result
            else:
                raise Exception("Async evaluation returned None")
                
    except Exception as e:
        print(f"🔄 Falling back to sync evaluation due to: {e}")
        # Fall back to synchronous evaluation
        return run_fallback_evaluation(
            transcript_text, topics_covered, duration, source_materials, slides_content
        )


def run_fallback_evaluation(
    transcript_text: str,
    topics_covered: str,
    duration: Optional[int] = None,
    source_materials: str = "",
    slides_content: str = ""
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Fallback synchronous evaluation without AI agents
    
    Args:
        transcript_text: The lecture transcript
        topics_covered: Comma-separated expected topics
        duration: Lecture duration in minutes
        source_materials: Reference materials for fact checking
        slides_content: Text content from presentation slides
        
    Returns:
        Tuple of (total_score, score_components, detailed_analysis)
    """
    score_components = {}
    detailed_analysis = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'evaluation_method': 'fallback_synchronous'
    }
    
    # 1. Correctness (30 points max) - Basic analysis
    word_count = len(transcript_text.split())
    if source_materials.strip():
        # Simple keyword overlap
        transcript_words = set(transcript_text.lower().split())
        source_words = set(source_materials.lower().split())
        overlap = len(transcript_words.intersection(source_words))
        total_unique = len(transcript_words.union(source_words))
        correctness_ratio = overlap / total_unique if total_unique > 0 else 0.5
    else:
        # Basic content density
        correctness_ratio = min(word_count / (duration * 10), 1.0) if duration else 0.5
    
    correctness_score = correctness_ratio * 30  # Scale to 30 max
    score_components['Correctness'] = correctness_score
    detailed_analysis['correctness'] = {
        'method': 'fallback_keyword_overlap',
        'correctness_ratio': correctness_ratio,
        'word_count': word_count
    }
    
    # 2. Engagement (20 points max) - Use sync function
    engagement_score, engagement_details = calculate_engagement_score_sync(
        transcript_text, slides_content
    )
    # Scale to 20 points max
    score_components['Engagement'] = min(engagement_score * 0.571, 20)
    detailed_analysis['engagement'] = engagement_details
    
    combined_content = transcript_text
    if source_materials:
        combined_content += "\n\n" + source_materials
    if slides_content:
        combined_content += "\n\n" + slides_content
    
    # 3. Topic Coverage (30 points max) - Synchronous
    from .topic_evaluator import calculate_topic_coverage_score
    topic_score, topic_details = calculate_topic_coverage_score(topics_covered, combined_content)
    # Scale to 30 points max
    score_components['Topic Coverage'] = min(topic_score * 3.0, 30)
    detailed_analysis['topic_coverage'] = topic_details
    
    # Calculate total score
    total_score = sum(score_components.values())
    detailed_analysis['total_score'] = total_score
    detailed_analysis['score_components'] = score_components
    
    return total_score, score_components, detailed_analysis