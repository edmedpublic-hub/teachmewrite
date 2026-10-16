from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lessons.services import ReportingService

class Command(BaseCommand):
    help = 'Sends progress reports to all parents'

    def handle(self, *args, **kwargs):
        # We only want to send reports for users who are 'students'
        students = User.objects.filter(profile__role='student')
        
        self.stdout.write(f"Starting report generation for {students.count()} students...")

        for student in students:
            try:
                report_text = ReportingService.generate_and_log_report(student.id)
                # Here is where you would call the WhatsApp API (like Twilio)
                # For now, we print it to the console to verify it works
                self.stdout.write(self.style.SUCCESS(f"Report Created for {student.username}"))
                print(f"--- MOCK SEND ---\n{report_text}\n----------------")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {student.username}: {e}"))