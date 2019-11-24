import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

REPORT_TEMPLATES_DIR = os.path.join(ROOT_DIR, 'templates')
UNIVERSAL_TEMPLATE_NAME = 'template_universal.docx'
OUTPUT_REPORTS_DIR = os.path.join(ROOT_DIR, 'output_reports')
