# backend/api/report_utils.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
from io import BytesIO
import json

class ReportGenerator:
    def __init__(self, user, progress_data):
        self.user = user
        self.progress_data = progress_data
    
    def generate_pdf_report(self):
        """Generate PDF report for parents/institutes"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'))
        story.append(Paragraph(f"Mastery Report - {self.user.get_full_name()}", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary table
        data = [
            ['Metric', 'Value'],
            ['Overall Mastery', f"{self.progress_data['overall_mastery']:.1f}%"],
            ['Lessons Mastered', f"{self.progress_data['mastered_lessons']}/{self.progress_data['total_lessons']}"],
            ['Total Time Spent', f"{self.progress_data.get('total_hours', 0)} hours"],
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_csv_report(self):
        """Generate CSV for institute analytics"""
        df = pd.DataFrame([self.progress_data])
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output
    
    def generate_whatsapp_message(self):
        """Generate WhatsApp-friendly message"""
        return f"""
🎓 *Mastery Report - {self.user.get_full_name()}*
📊 *Overall Mastery:* {self.progress_data['overall_mastery']:.1f}%
✅ *Lessons Mastered:* {self.progress_data['mastered_lessons']}/{self.progress_data['total_lessons']}
⭐ *Streak:* {self.progress_data.get('streak_days', 0)} days

View full report: {self.progress_data.get('report_link', '#')}
        """
    
    def generate_email_html(self):
        """Generate HTML email template"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 20px; }}
        .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ background: #4caf50; height: 30px; width: {self.progress_data['overall_mastery']}%; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MasteryAI Progress Report</h1>
            <p>{self.user.get_full_name()}</p>
        </div>
        <div class="content">
            <div class="metric">
                <strong>Overall Mastery</strong>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <p>{self.progress_data['overall_mastery']:.1f}% Complete</p>
            </div>
            <div class="metric">
                <strong>Lessons Mastered</strong>
                <p>{self.progress_data['mastered_lessons']} out of {self.progress_data['total_lessons']}</p>
            </div>
            <div class="metric">
                <strong>Current Streak</strong>
                <p>{self.progress_data.get('streak_days', 0)} days</p>
            </div>
        </div>
        <div class="footer">
            <p>MasteryAI - English Writing Mastery for Pakistan</p>
            <p>Generated on {self.progress_data['generated_at'][:10]}</p>
        </div>
    </div>
</body>
</html>
        """