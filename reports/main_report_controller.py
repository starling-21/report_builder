"""
like a Facade Pattern, but for procedural calls

handle main process for report creation
- proceed user's input data
- proceed user's data modifications (servicemen_chain, optional)
- report content data preparations
- report document generation
"""
from .models import Serviceman

from . import report_content_util
from . import document_generator

def generate_report(request, serviceman_id, members_chain_id_list=None):
    """
    Generate report file filled by merge dict based on input params
    :param serviceman_id:
    :param report_id:
    :param members_chain_id_list: serviceman identifiers list
    :return: report file path
    """
    report_merge_dict = {}
    serviceman = Serviceman.objects.get(id=serviceman_id)

    if members_chain_id_list is None:
        members_chain_id_list = report_content_util.get_servicemen_chain_id_list(serviceman_id)

    report_merge_dict = report_content_util.get_report_merge_dict(request, serviceman_id, members_chain_id_list)

    # print("GLOBAL MERGE DICT:", global_merge_dict)
    for k, v in report_merge_dict.items():
        print("{} : {}".format(k, v))

    report_filepath = document_generator.create_docx_document(report_merge_dict)

    return report_filepath


