"""defines project CONSTS for reports templates and final reports directory"""
import os
import reports

reports_app_path = os.path.dirname(reports.__file__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

REPORT_TEMPLATES_DIR = os.path.join(reports_app_path, 'templates')
UNIVERSAL_TEMPLATE_NAME = 'template_universal.docx'

OUTPUT_REPORTS_DIR = os.path.join(ROOT_DIR, '../output_reports')
