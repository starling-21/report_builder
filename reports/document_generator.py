"""
generates docx reports based on input merge dictionary
based on report tier level and choose correspondent template
"""
from definitions import OUTPUT_REPORTS_DIR, REPORT_TEMPLATES_DIR, UNIVERSAL_TEMPLATE_NAME
from datetime import datetime
from mailmerge import MailMerge
import os

# //TODO implement main methods
def create_docx_document(merge_dict):
    """
    generate report document from merge dict
    :param merge_dict: dictionary for MailMerge library for document generation
    :param template_name: default name is in definitions.py file
    :return:  generated document path
    """

    template_name = UNIVERSAL_TEMPLATE_NAME
    if not os.path.exists(OUTPUT_REPORTS_DIR):
        try:
            os.mkdir(OUTPUT_REPORTS_DIR)
        except OSError:
            print("Creation of the directory %s failed" % OUTPUT_REPORTS_DIR)
        else:
            print("Successfully created the directory %s " % OUTPUT_REPORTS_DIR)
    template_path = os.path.join(REPORT_TEMPLATES_DIR, template_name)
    document = MailMerge(template_path)
    print("Merge fields at {} document: {}".format(template_name, document.get_merge_fields()))
    document.merge(**merge_dict)
    now = datetime.now()
    merged_file_path = os.path.join(OUTPUT_REPORTS_DIR, now.strftime("%d %H_%M_%S") + '_report.docx')
    document.write(merged_file_path)
    return merged_file_path
