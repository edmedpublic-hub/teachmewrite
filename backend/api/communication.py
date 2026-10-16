# backend/api/communication.py

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import requests
import json

class CommunicationManager:
    
    @staticmethod
    def send_email_report(to_email, subject, html_content, pdf_attachment=None):
        """Send email report with optional PDF attachment"""
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.content_subtype = "html"
        
        if pdf_attachment:
            email.attach(f'report_{to_email}.pdf', pdf_attachment, 'application/pdf')
        
        return email.send()
    
    @staticmethod
    def send_whatsapp_message(phone_number, message):
        """Send WhatsApp message (requires WhatsApp Business API)"""
        # For now, placeholder for Twilio or WhatsApp Business API
        # You'll need to sign up for WhatsApp Business API
        whatsapp_api_url = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        # Uncomment when you have WhatsApp API configured
        # response = requests.post(whatsapp_api_url, headers=headers, json=data)
        # return response.status_code == 200
        
        # For now, return True for testing
        return True
    
    @staticmethod
    def send_bulk_notifications(users, message, method='email'):
        """Send bulk notifications to multiple users"""
        results = []
        for user in users:
            if method == 'email':
                success = CommunicationManager.send_email_report(
                    user.email, 
                    "MasteryAI Update", 
                    message
                )
            elif method == 'whatsapp' and hasattr(user, 'profile') and user.profile.phone:
                success = CommunicationManager.send_whatsapp_message(
                    user.profile.phone,
                    message
                )
            results.append({'user': user.username, 'success': success})
        return results