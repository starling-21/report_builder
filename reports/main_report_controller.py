"""
like a Facade Pattern, but for procedural calls

handle main process for report creation
- proceed user's input data
- proceed user's data modifications (servicemen_chain, optional)
- report content data preparations
- report document generation
"""
from reports.definitions import OUTPUT_REPORTS_DIR, REPORT_TEMPLATES_DIR, UNIVERSAL_TEMPLATE_NAME
from datetime import datetime
from mailmerge import MailMerge
import os
from . import report_content_util


def generate_report(request):
    """
    Generate report file filled by merge dict based on input params
    request: request with data for report filling
    :return: report file path
    """
    report_merge_dict = report_content_util.get_report_merge_dict(request)
    # print("GLOBAL MERGE DICT:", report_merge_dict)
    # for k, v in report_merge_dict.items():
    #     print("{} : {}".format(k, v))

    report_filepath = create_docx_document(report_merge_dict)

    return report_filepath


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

    template_path = os.path.join(REPORT_TEMPLATES_DIR, template_name)
    document = MailMerge(template_path)
    # print("Merge fields at {} document: {}".format(template_name, document.get_merge_fields()))
    document.merge(**merge_dict)
    now = datetime.now()
    merged_file_path = os.path.join(OUTPUT_REPORTS_DIR, now.strftime("%d %H_%M_%S") + '_report.docx')
    document.write(merged_file_path)
    return merged_file_path
