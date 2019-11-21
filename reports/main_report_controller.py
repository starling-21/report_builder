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
from . import report_forms_util


def generate_report(request, serviceman_id, report_id, members_chain_id_list=None):
    """
    Generate report file filled by prepared dict
    :param serviceman_id:
    :param report_id:
    :param members_chain_id_list: serviceman identifiers list
    :return:
    """
    #TODO's
    # 1) prepare merge dictionary for report
    # 2) figure out template name
    # 3) create document by merging

    global_merge_dict = {}

    serviceman = Serviceman.objects.get(id=serviceman_id)

    if members_chain_id_list is None:
        members_chain_id_list = report_content_util.get_servicemen_chain_id_list(serviceman_id)

    global_merge_dict = report_content_util.get_report_merge_dict(request, serviceman_id, members_chain_id_list)
    print("GLOBAL MERGE DICT:", global_merge_dict)

    #TODO impolementaion required
    return ""



