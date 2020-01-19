"""
-- this file purpose is to prepare data structure and pass them into document generator module as final merge dictionary

-- tiers handling should be specified here to let document generator choose right document report template

-- serves as middleware mechanism for report's service_members chain modification


2nd OPTION:
accept: request  django backend session store extra data (user id, report id and service_members chain)
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


global_merge_dict = {}

def get_report_merge_dict(request):
    """
    creates user pairs dictionary for every report tier --> {tier:[footer_user, header_user]}
    iterate throught tiers dict and put data to global_merge_dict, by changing merge dict keys like {key_<tier_number>:value_to_merge}

    :param request: post request from filled form
    :return: global merge dictionary
    """
    try:
        global global_merge_dict

        serviceman_chain = request.session['serviceman_chain']
        serviceman_id = serviceman_chain[0].id


        user_pairs_dict = convert_members_chain_to_pairs_dict(serviceman_chain)
        for tier, users in user_pairs_dict.items():
            from_user = users[0]
            to_user = users[1]

            # footer preparation
            footer_dict = get_footer_data(from_user)
            footer_dict = modify_dict_keys(footer_dict, tier)
            global_merge_dict.update(footer_dict)

            # header preparation
            header_dict = get_header_data(to_user)
            header_dict = modify_dict_keys(header_dict, tier)
            global_merge_dict.update(header_dict)

            # report body text preparation
            if tier == 0:
                report_body_dict = compose_main_report_body_from_post_request(request.POST.copy())
                # print("report_body_dict:\n", report_body_dict)
            elif tier >= 1:
                report_body_dict = get_secondary_report_body(serviceman_id)
            report_body_dict = modify_dict_keys(report_body_dict, tier)
            global_merge_dict.update(report_body_dict)
    except Exception as e:
        print(e)
        global_merge_dict = {'error':'report_content_util->get_report_merge_dict'}
    finally:
        return global_merge_dict


def compose_main_report_body_from_post_request(input_form_data_dict):
    """
    parse submitted form data, transferred here as POST request
    :param input_form_data_dict: POST request field contains amount of fields to collect together
    :return: returns report body text as dictionary with hard_coded key - "body_tier".
    """
    report_body_dict = {}
    report_body_text = ""
    form_fields_amount = int(input_form_data_dict.get('fields_counter'))
    for i in range(0, form_fields_amount + 1):
        try:
            # TODO kostul, needs refactoring
            test_date_conversion_error = datetime.strptime(input_form_data_dict.get(str(i)),
                                                           "%Y-%m-%d").date()  # DO nOt delete
            report_body_text += convert_datetime_as_day_month_year(input_form_data_dict.get(str(i)))
        except ValueError:
            report_body_text += input_form_data_dict.get(str(i))
        except Exception as e:
            print(e)
            print('error compose_main_report_body_from_post_request')
    print("REPORT BODY:", report_body_dict)
    report_body_dict['body_tier'] = report_body_text
    return report_body_dict


def get_secondary_report_body(serviceman_id):
    """returns report dictionary contains next body template like this:
        Клопочу по суті рапорту полковника Степана Колотило.
        :return dict {merger_key: value}
    """
    global global_merge_dict

    report_body_dict = {}
    report_body_text = ""
    serviceman = Serviceman.objects.get(id=serviceman_id)
    first_body_word = 'Клопочу'
    if 'Прошу' in global_merge_dict['body_tier_0'].split()[0]:
        first_body_word = 'Клопочу'
    elif 'Доповiдаю' in global_merge_dict['body_tier_0'].split()[0]:
        first_body_word = 'Доповідаю'

    report_body_text += first_body_word + " по суті рапорту " + serviceman.rank.for_name + " " + serviceman.get_full_name_for() + "."
    report_body_dict['body_tier'] = report_body_text
    return report_body_dict


def modify_dict_keys(dictionary, tier):
    """
    adds tier value to every key in a dictionary
    example: key=abc, tier=2 --> abc_2
    """
    result = {}
    for key, value in dictionary.items():
        result[key + '_' + str(tier)] = value
    return result


def convert_members_chain_to_pairs_dict(servicemen_chain_list):
    """
    convert members list to chain member pairs
    :param servicemen_chain_list: users objects list
    :return: servicemen tiers chain dictionary {'report tier number':[users pair]}
    """
    tiers_dict = {}
    if len(servicemen_chain_list) < 2:
        return None
    elif len(servicemen_chain_list) == 2:
        tiers_dict[0] = [servicemen_chain_list[0], servicemen_chain_list[1]]
    elif len(servicemen_chain_list) > 2:
        for i in range(0, len(servicemen_chain_list) - 1):
            tiers_dict[i] = [servicemen_chain_list[i], servicemen_chain_list[i + 1]]
    return tiers_dict


def get_servicemen_chain_list(report_id, serviceman=None):
    """return report's service members chain based on report type
       return servicemen objects list
    """
    report = Report.objects.get(id=report_id)
    users_list = []

    if report.type == 'regular':
        users_list = get_full_servicemen_chain_list(serviceman)
    elif report.type == 'custom':
        users_list.append(get_chief_or_his_deputy_by_position(report.default_footer_position))
        users_list.append(get_chief_or_his_deputy_by_position(report.default_header_position))

    return users_list


def get_full_servicemen_chain_list(serviceman):
    """return service members chain from initiator too the top level supervisor
       RECURSIVE METHOD, be carefull :)
       return servicemen objects list
    """
    users_list = []
    serviceman = get_temp_deputy_if_exists(serviceman)
    users_list.append(serviceman)
    next_supervisor = get_supervisor_for(serviceman)
    if next_supervisor is not None:
        users_list.extend(get_full_servicemen_chain_list(next_supervisor))
    return users_list


def get_chief_or_his_deputy_by_position(position):
    """
    get serviceman or his deputy by position
    :param position:
    :return:  if there is no deputy, return hist boss
    """
    if position.supervisor:
        default_serviceman = Serviceman.objects.get(position=position)
        try:
            first_priority_position = Position.objects.get(unit=position.unit, temp_supervisor=True)
            first_priority_position.temp_supervisor = True
            first_priority_serviceman = Serviceman.objects.filter(position=first_priority_position).first()
            if first_priority_serviceman:
                return first_priority_serviceman
        except Exception as e:
            pass
            # print(e)

    return default_serviceman

def get_temp_deputy_if_exists(serviceman):
    """
    check for service member temporary deputy if he exists
    :param serviceman:
    :return: deputy or normal unit chief
    """
    if serviceman.position.supervisor == True:
        return get_chief_or_his_deputy_by_position(serviceman.position)
    return serviceman


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
        'footer_position_tier': full_position,
        'footer_rank_tier': rank,
        'footer_username_tier': full_name,
        'date_line_tier': footer_date_line
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
        'header_position_tier': full_position,
        'header_rank_tier': rank,
        'header_username_tier': full_name,
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


def convert_datetime_as_day_month_year(date_str, with_no_year=False):
    """return properly formatted date line to report for visual representation"""
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
