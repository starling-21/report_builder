"""
-- this file purpose is to prepare data structure and pass them into document generator module as final merge dictionary

-- tiers handling should be specified here to let document generator choose right document report template

-- serves as middleware mechanism for report's service_members chain modification

INPUT DATA:

1st OPTION:
accept user id (based on incoming user_id generates service_men chain to the top supervisor)
--> returns it for user modifications //TODO chose best data representation to fill in this data into html form

2nd OPTION:
accept user id, report id and service_members chain (optional)
--> generate final data content dictionary for report's document generator


OUPUT DATA:
1) report merge dict
2) report tier number as extra option (for doc template generator convenience)
"""

from reports.models import Serviceman
from reports.models import Position
from reports.models import Report
from django.db.models import Q
from datetime import datetime


def get_global_report_merge_dict_test_1(serviceman):
    """iterate throught tier's user pairs (if serviceman has a supervisor) and return data for global_merge_dict
        Format: {tier:{report dict}}
    """
    try:
        global_merge_dict = {}
        user_pairs_dict = get_tier_users_pairs(serviceman)
        for tier, users in user_pairs_dict.items():
            from_user = users[0]
            to_user = users[1]

            footer_dict = get_footer_data(from_user)
            footer_dict = append_to_dict_keys(footer_dict, tier)
            global_merge_dict.update(footer_dict)

            header_dict = get_header_data(to_user)
            header_dict = append_to_dict_keys(header_dict, tier)
            global_merge_dict.update(header_dict)
    except:
        global_merge_dict = None
    finally:
        return global_merge_dict


def get_report_body(input_form_data):
    """
    parse submitted form data, transferred here as POST request
    returns report body text as string.
    """
    report_body = ""
    form_fields_amount = int(input_form_data.get('fields_counter'))
    for i in range(0, form_fields_amount + 1):
        try:
            test_date_conversion = datetime.strptime(input_form_data.get(str(i)), "%Y-%m-%d").date()
            report_body += datetime_as_day_month_year(input_form_data.get(str(i)))
        except ValueError:
            report_body += input_form_data.get(str(i))
    print("REPORT BODY:", report_body)
    return report_body


def get_report_body_template(serviceman_id):
    """returns report body template like this:
        Клопочу по суті рапорту полковника Степана Колотило.
    """
    serviceman = Serviceman.objects.get(id=serviceman_id)
    return "Клопочу по суті рапорту " + serviceman.rank.for_name + " " + serviceman.get_full_name_for() + "."


def append_to_dict_keys(dictionary, tier):
    """adds tier value to every key in a dictionary"""
    result = {}
    for key, value in dictionary.items():
        result[key + str(tier)] = value
    return result


def get_tier_users_pairs(serviceman):
    """returns dictionary of paired users for report. {tier:(FROM_user, TO_user),....} or NONE"""
    users_chain = get_servicemen_chain_as_list(serviceman)
    tiers_dict = {}
    if len(users_chain) < 2:
        return None
    elif len(users_chain) == 2:
        tiers_dict[0] = (users_chain[0], users_chain[1])
    elif len(users_chain) > 2:
        for i in range(0, len(users_chain) - 1):
            tiers_dict[i] = (users_chain[i], users_chain[i + 1])
    return tiers_dict


def get_servicemen_chain_as_list(serviceman):
    """return service members chain from initiator too the top level supervisor
       RECURSIVE METHOD, be carefull :)
    """
    users_list = []
    users_list.append(serviceman)
    next_supervisor = get_supervisor_for(serviceman)
    if next_supervisor is not None:
        users_list.extend(get_servicemen_chain_as_list(next_supervisor))
    return users_list


def get_servicemen_chain_as_dict(serviceman):
    """return service members chain from initiator too the top level supervisor
       RECURSIVE METHOD, be carefull :)
    """
    users_dict = {}
    users_dict[serviceman.id] = serviceman
    next_supervisor = get_supervisor_for(serviceman)
    if next_supervisor is not None:
        users_dict.update(get_servicemen_chain_as_dict(next_supervisor))
    return users_dict


def get_footer_data(serviceman):
    """returns footer data dict for certain serviceman"""
    position = serviceman.position
    unit = serviceman.unit
    units_chain = unit.get_all_parents()
    rank = serviceman.rank.__str__()
    full_name = serviceman.get_full_name()

    full_position = get_full_position(position.__str__(), units_chain)
    footer_date_line = get_current_date_line()

    footer_dict = {
        'footer_position_tier_': full_position,
        'footer_rank_tier_': rank,
        'footer_username_tier_': full_name,
        'date_line_tier_': footer_date_line
    }

    # print_footer(footer_dict)
    return footer_dict


def get_header_data(serviceman):
    """returns header data dict for certain serviceman"""
    position = serviceman.position.get_to_position()
    unit = serviceman.unit
    units_chain = unit.get_all_parents()
    rank = serviceman.rank.to_name
    full_name = serviceman.get_full_name_to()

    full_position = get_full_position(position, units_chain)

    header_dict = {
        'header_position_tier_': full_position,
        'header_rank_tier_': rank,
        'header_username_tier_': full_name,
    }

    # print_header(header_dict)
    return header_dict


def get_full_position(main_position, units_chain):
    """complete initial main_position with units list user belongs to"""
    full_position = main_position
    position_tail = ""

    if (len(units_chain) > 0): position_tail = units_chain[len(units_chain) - 1].name
    for i in range(0, len(units_chain) - 1):
        full_position = full_position + " " + units_chain[i].name

    if (position_tail is not ""):
        full_position = full_position + "\n" + position_tail
    return full_position


def get_supervisor_for(serviceman):
    """return supervisor for certain user"""
    # serviceman = serviceman
    is_supervisor = serviceman.position.supervisor or serviceman.position.temp_supervisor
    if is_supervisor:
        unit_supervisor_position = Position.objects.filter(Q(unit=serviceman.unit.parent_unit),
                                                           Q(temp_supervisor=True) | Q(supervisor=True)).first()
    else:
        unit_supervisor_position = Position.objects.filter(Q(unit=serviceman.unit),
                                                           Q(temp_supervisor=True) | Q(supervisor=True)).first()
    supervisor = Serviceman.objects.filter(position=unit_supervisor_position).first()
    return supervisor


def get_serviceman(user_id):
    """returns serviceman vith select related fields: rank, unit and position"""
    return Serviceman.objects.filter(pk=user_id).select_related('rank', 'unit', 'position').first()


def get_report_tiers_count(serviceman):
    """return report TIER level for serviceman"""
    tiers_chain = serviceman.unit.get_all_parents(include_self=True)
    tiers_counter = len(tiers_chain)
    is_supervisor = serviceman.position.supervisor or serviceman.position.temp_supervisor
    if is_supervisor:
        tiers_counter -= 1
    print("units chain for: {}, counter: {}, list: {}".format(serviceman, tiers_counter, tiers_chain))
    return tiers_counter


def get_current_date_line():
    """return properly formated date line for report"""
    monthes = {
        1: "січня",
        2: "лютого",
        3: "березня",
        4: "квітня",
        5: "травня",
        6: "червня",
        7: "липня",
        8: "серпня",
        9: "вересня",
        10: "жовтня",
        11: "листопада",
        12: "грудня",
    }

    month_numb = datetime.now().month
    year = datetime.now().year
    return '"___"' + ' ' + monthes[month_numb] + ' ' + str(year) + ' ' + 'року'


def datetime_as_day_month_year(date_str, with_no_year=False):
    """return properly formated date line for report"""
    temp_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    monthes = {
        1: "січня",
        2: "лютого",
        3: "березня",
        4: "квітня",
        5: "травня",
        6: "червня",
        7: "липня",
        8: "серпня",
        9: "вересня",
        10: "жовтня",
        11: "листопада",
        12: "грудня",
    }
    day_numb = temp_date.day
    month_numb = temp_date.month
    year = temp_date.year
    if with_no_year:
        return str(day_numb) + ' ' + monthes[month_numb]
    return str(day_numb) + ' ' + monthes[month_numb] + ' ' + str(year)


def print_footer(footer_dict):
    print("\n\nFROM:______ %s______" % footer_dict['footer_username_tier_'])
    for k, v in footer_dict.items():
        print("{} : {}".format(k, v))


def print_header(headeer_dict):
    print("\n\nTO  :______ %s______" % headeer_dict['header_username_tier_'])
    for k, v in headeer_dict.items():
        print("{} : {}".format(k, v))
