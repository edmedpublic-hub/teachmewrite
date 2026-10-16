# backend/api/views/ai_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lessons.models import Tier


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def diagnose_tier(request):
    """Analyze student's writing and recommend appropriate tier"""
    writing_sample = request.data.get('writing_sample', '')
    if not writing_sample:
        return Response({'error': 'Writing sample required'}, status=400)
    
    word_count = len(writing_sample.split())
    sentence_count = len(writing_sample.split('.'))
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    if word_count < 100 or avg_sentence_length < 10:
        recommended_tier = Tier.BASIC
        confidence = 0.8
        reasoning = "Short writing sample with simple sentence structures"
    elif word_count < 300 or avg_sentence_length < 15:
        recommended_tier = Tier.INTERMEDIATE
        confidence = 0.7
        reasoning = "Moderate length with developing complexity"
    elif word_count < 500 or avg_sentence_length < 20:
        recommended_tier = Tier.ADVANCED
        confidence = 0.6
        reasoning = "Good length with varied sentence structures"
    else:
        recommended_tier = Tier.PROFESSIONAL
        confidence = 0.7
        reasoning = "Extended writing with sophisticated structures"
    
    # TODO: Integrate Gemini API for more accurate analysis
    # from google import generativeai
    # gemini_response = generativeai.generate_content(writing_sample)
    
    return Response({
        'recommended_tier': recommended_tier,
        'tier_display': Tier(recommended_tier).label,
        'confidence_score': confidence,
        'analysis': {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'reasoning': reasoning
        },
        'message': f'Based on your writing analysis, we recommend starting at the {Tier(recommended_tier).label} level.'
    })