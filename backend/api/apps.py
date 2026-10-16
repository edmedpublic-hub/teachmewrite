from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'MasteryAI REST API'
    
    def ready(self):
        """Initialize API when app is ready"""
        # Import signal handlers if any
        pass