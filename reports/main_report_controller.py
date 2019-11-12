"""
like a Facade Pattern, but for procedural calls

handle main process for report creation
- proceed user's input data
- proceed user's data modifications (servicemen_chain, optional)
- report content data preparations
- report document generation
"""
from .models import Serviceman

from . import report_content_util as content_util
from . import report_form_util as form_util


def proceed_report_generation(serviceman_id, report_id, users_tier_chain=None):
        serviceman = Serviceman.objects.get(id=serviceman_id)

        if users_tier_chain is None:
            users_tier_chain = content_util.get_servicemen_chain_as_dict(serviceman)

