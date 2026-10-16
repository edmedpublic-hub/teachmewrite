# backend/api/views/certificate_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lessons.models import Certificate, TierProgress, Tier
from ..serializers import CertificateSerializer
import hashlib
import time


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for certificates"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a certificate for completed tier"""
        tier = request.data.get('tier')
        
        if not tier or tier.upper() not in [t.value for t in Tier]:
            return Response({'error': 'Invalid tier'}, status=400)
        
        # Check if tier is completed
        try:
            tier_progress = TierProgress.objects.get(user=request.user, tier=tier.upper())
            if not tier_progress.is_completed:
                return Response({'error': 'Tier not completed yet'}, status=400)
        except TierProgress.DoesNotExist:
            return Response({'error': 'Tier progress not found'}, status=404)
        
        # Check if certificate already exists
        existing = Certificate.objects.filter(user=request.user, tier=tier.upper()).first()
        if existing:
            return Response({
                'certificate': CertificateSerializer(existing).data,
                'message': 'Certificate already exists'
            })
        
        # Generate unique certificate number
        cert_number = hashlib.md5(f"{request.user.id}{tier}{time.time()}".encode()).hexdigest()[:16].upper()
        
        certificate = Certificate.objects.create(
            user=request.user,
            tier=tier.upper(),
            certificate_number=cert_number
        )
        
        return Response({
            'certificate': CertificateSerializer(certificate).data,
            'message': f'Certificate generated for {Tier(tier.upper()).label} tier'
        })
    
    @action(detail=False, methods=['get'])
    def verify(self, request):
        """Verify a certificate by code"""
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Verification code required'}, status=400)
        
        try:
            certificate = Certificate.objects.get(verification_code=code.upper())
            certificate.is_verified = True
            certificate.save()
            
            return Response({
                'valid': True,
                'certificate': CertificateSerializer(certificate).data
            })
        except Certificate.DoesNotExist:
            return Response({'valid': False, 'error': 'Invalid certificate code'}, status=404)