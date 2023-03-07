def automation_data(initial_data):
    automation_type = initial_data.get("type")
    print(automation_type)
    is_automate_paid = "paid" in initial_data
    first_name = initial_data.get("first_name")
    last_name = initial_data.get("last_name")
    email = initial_data.get("email")
    password = initial_data.get("password")
    country = initial_data.get("country")
    state = initial_data.get("state")
    phone_number = initial_data.get("phone_number")
    area_code = initial_data.get("area_code")
    postal_code = initial_data.get("postal_code")
    address = initial_data.get("address")
    email_fake = initial_data.get("email_fake")
    phone_number_fake = initial_data.get("phone_number_fake")
    ein = initial_data.get("ein")
    ssn = initial_data.get("ssn")
    company_name = initial_data.get("company_name")
    data = {}
    if is_automate_paid and automation_type == "MC+DOT":
        data = {
            "step_9": {
                "create_password": password,
                "confirm_password": password,
                "security_question_1": "What was my high school mascot?",
                "security_answer_1": "bear",
                "security_question_2": "What is my least favorite vegetable?",
                "security_answer_2": "ford",
                "security_question_3": "What is my pet name?",
                "security_answer_3": "baby",
            },
            "step_11": {
                "application_contact_type": "Applicant Representative",
                "application_contact_first_name": first_name,
                # 'application_contact_middle_name': '',
                "application_contact_last_name": last_name,
                # 'application_contact_suffix': '',
                "application_contact_title": "owner",
                "application_contact_country": country,
                "application_contact_street_address_line_1": address,
                # 'application_contact_street_address_line_2': address_l2,
                # 'application_contact_city': '',
                # 'application_contact_state_or_province': '',
                "application_contact_postal_code": postal_code,
                "application_contact_telephone_number": {
                    "country_code": country,
                    "area_code": area_code,
                    "phone_number": phone_number_fake,
                    "extra_phone_number": "",
                },
                # 'application_contact_fax_number': {
                #     'country_code': '',
                #     'area_code': '',
                #     'phone_number': '',
                # },
                # 'application_contact_cell_phone_number': {
                #     'country_code': '',
                #     'area_code': '',
                #     'phone_number': '',
                # },
                "application_contact_email_address": email_fake,
                "application_contact_confirm_email_address": email_fake,
                "application_contact_preferred_contact_method": "US Mail",
            },
            "step_13": {
                "checked": False,
            },
            "step_14": {
                "legal_business_name": company_name,
            },
            "step_16": {
                "checked": True,
            },
            "step_17": {
                "mailing_address_sameas_principal": True,
            },
            "step_18": {
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_19": {},
            "step_20": {
                "checked": False,
            },
            "step_21": {
                "checked": "Corporation (State of Incorporation)",
                "choose_one": state.upper(),
            },
            "step_22": {
                "checked": "Owned/controlled by citizen of United States",
            },
            "step_23": {
                "company_contact_1_checked": True,
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "email": email,
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_24": {
                "country": country,
                "street_address_or_route_number_line_1": address,
                # 'street_address_or_route_number_line_2': address_l2,
                "postal_code": postal_code,
                "blank_click": True,
            },
            "step_27": {
                "checked": False,
            },
            "step_28": {
                "checked": True,
            },
            "step_29": {
                "checked": True,
            },
            "step_30": {
                "checked": "Other Non-Hazardous Freight",
            },
            "step_31": {
                "checked": True,
            },
            "step_32": {
                "checked": False,
            },
            "step_33": {
                "checked": False,
            },
            "step_34": {
                "checked": False,
            },
            "step_35": {
                "checked": False,
            },
            "step_36": {
                "checked": False,
            },
            "step_37": {
                "checked": False,
            },
            "step_38": {
                "checked": False,
            },
            "step_39": {
                "checked": "General Freight",
            },
            "step_42": {
                "non_cmv_property": 0,
            },
            "step_43": {
                "straight_trucks": {
                    "owned": 1,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "truck_tractors": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "trailers": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "iep_trailer_chassis_only": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                    "serviced": 0,
                },
            },
            "step_44": {
                "canada": 0,
                "mexico": 0,
            },
            "step_45": {
                "questionCode_B0061P060081S06008_Q06048_id": 1,
            },
            "step_46": {
                "questionCode_B0061P060091S06009_Q06049_id": 0,
            },
            "step_49": {
                "questionCode_B0071P070021S07002_Q07001_id": 1,
                "questionCode_B0071P070021S07002_Q07002_id": 0,
            },
            "step_50": {
                "questionCode_B0071P070051S07003_Q07003_id": 0,
                "questionCode_B0071P070051S07003_Q07004_id": 0,
            },
            "step_51": {
                "questionCode_B0071P070061S07004_Q07005_id": 0,
            },
            "step_52": {
                "canada": 0,
                "mexico": 0,
            },
            "step_55": {
                "checked": True,
            },
            "step_58": {
                "checked": False,
            },
            "step_61": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_69": {
                "electronic_signature_application_password": password,
            },
            "step_72": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_74": {
                "checked": True,
            },
            "step_75": {
                "user_id": email,
                "email": email,
                "password": password,
                "method_of_contact": "US Mail",
            },
            "step_76": {
                "checked": True,
            },
            "step_78": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_80": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_83": {},
        }
    elif is_automate_paid and automation_type == "Broker":
        data = {
            "step_9": {
                "create_password": password,
                "confirm_password": password,
                "security_question_1": "What was my high school mascot?",
                "security_answer_1": "bear",
                "security_question_2": "What is my least favorite vegetable?",
                "security_answer_2": "ford",
                "security_question_3": "What is my pet name?",
                "security_answer_3": "baby",
            },
            "step_11": {
                "application_contact_type": "Applicant Representative",
                "application_contact_first_name": first_name,
                # 'application_contact_middle_name': '',
                "application_contact_last_name": last_name,
                # 'application_contact_suffix': '',
                "application_contact_title": "owner",
                "application_contact_country": country,
                "application_contact_street_address_line_1": address,
                # 'application_contact_street_address_line_2': address_l2,
                # 'application_contact_city': '',
                # 'application_contact_state_or_province': '',
                "application_contact_postal_code": postal_code,
                "application_contact_telephone_number": {
                    "country_code": country,
                    "area_code": area_code,
                    "phone_number": phone_number_fake,
                    "extra_phone_number": "",
                },
                # 'application_contact_fax_number': {
                #     'country_code': '',
                #     'area_code': '',
                #     'phone_number': '',
                # },
                # 'application_contact_cell_phone_number': {
                #     'country_code': '',
                #     'area_code': '',
                #     'phone_number': '',
                # },
                "application_contact_email_address": email_fake,
                "application_contact_confirm_email_address": email_fake,
                "application_contact_preferred_contact_method": "US Mail",
            },
            "step_13": {
                "checked": False,
            },
            "step_14": {
                "legal_business_name": company_name,
            },
            "step_16": {
                "checked": True,
            },
            "step_17": {
                "mailing_address_sameas_principal": True,
            },
            "step_18": {
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_19": {},
            "step_20": {
                "checked": False,
            },
            "step_21": {
                "checked": "Corporation (State of Incorporation)",
                "choose_one": state.upper(),
            },
            "step_22": {
                "checked": "Owned/controlled by citizen of United States",
            },
            "step_23": {
                "company_contact_1_checked": True,
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "email": email,
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_24": {
                "country": country,
                "street_address_or_route_number_line_1": address,
                # 'street_address_or_route_number_line_2': address_l2,
                "postal_code": postal_code,
                "blank_click": True,
            },
            "step_27": {
                "checked": False,
            },
            "step_28": {
                # 'checked': True,
                "checked": False,
            },
            "step_29": {
                # 'checked': True,
                "checked": False,
            },
            # - new step 30 data -
            "step_30": {
                "checked": True,
            },
            "step_31": {
                "checked": False,
            },
            "step_32": {
                "checked": False,
            },
            "step_33": {
                "checked": False,
            },
            "step_34": {
                "checked": False,
            },
            "step_35": {
                "checked": False,
            },
            "step_36": {
                "checked": False,
            },
            "step_37": {
                "checked": False,
            },
            "step_38": {
                "checked": False,
            },
            "step_39": {"checked": "General Freight"},
            "step_58": {
                "checked": False,
            },
            "step_61": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_69": {
                "electronic_signature_application_password": password,
            },
            "step_72": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_74": {
                "checked": True,
            },
            "step_75": {
                "user_id": email,
                "email": email,
                "password": password,
                "method_of_contact": "US Mail",
            },
            "step_76": {
                "checked": True,
            },
            "step_78": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_80": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_83": {},
        }
    elif automation_type == "Private+Inter":
        data = {
            'step_9': {
                'create_password': password,
                'confirm_password': password,
                'security_question_1': 'What was my high school mascot?',
                'security_answer_1': 'bear',
                'security_question_2': 'What is the make of my first car?',
                'security_answer_2': 'ford',
                'security_question_3': 'What is my pet name?',
                'security_answer_3': 'baby',
            },
            'step_11': {
                'application_contact_type': 'Applicant Representative',
                'application_contact_first_name': first_name,
                'application_contact_last_name': last_name,
                'application_contact_title': 'owner',
                'application_contact_country': country,
                'application_contact_street_address_line_1': address,
                'application_contact_postal_code': postal_code,
                'application_contact_telephone_number': {
                    'country_code': country,
                    'area_code': area_code,
                    'phone_number': phone_number_fake,
                    'extra_phone_number': '',
                },
                'application_contact_email_address': email_fake,
                'application_contact_confirm_email_address': email_fake,
                'application_contact_preferred_contact_method': 'US Mail',
            },
            'step_13': {
                'checked': False,
            },
            'step_14': {
                'legal_business_name': company_name,
            },
            'step_16': {
                'checked': True,
            },
            'step_17': {
                'mailing_address_sameas_principal': True,
            },
            'step_18': {
                'country': country,
                'area_code': area_code,
                'phone_number': phone_number_fake
            },
            'step_19': {},
            'step_20': {
                'checked': False,
            },
            'step_21': {
                'checked': 'Limited Liability Company',
                'choose_one': state.upper(),
            },
            'step_22': {
                'checked': 'Owned/controlled by citizen of United States',
            },
            'step_23': {
                'company_contact_1_checked': True,
                'first_name': first_name,
                'last_name': last_name,
                'title': 'owner',
                'email': email_fake,
                'country': country,
                'area_code': area_code,
                'phone_number': phone_number_fake
            },
            'step_24': {
                'country': country,
                'street_address_or_route_number_line_1': address,
                'postal_code': postal_code,
            },
            'step_27': {
                'checked': False,
            },
            'step_28': {
                'checked': True,
                # 'checked': False,
            },
            'step_29': {
                # 'checked': True,
                'checked': False,
            },
            #                - new step 30 data -
            'step_30': {
                'checked': True,
            },
            'step_31': {
                # 'checked': False,
                'checked': True,
            },
            'step_32': {
                # 'checked': False,
                'checked': True,
            },
            'step_33': {
                'checked': False,
            },
            'step_34': {
                # 'checked': False,
                    'checked': True,
            },
            'step_35': {
                'checked': False,
            },
            'step_36': {
                'checked': False,
            },
            'step_37': {
                'checked': False,
            },
            'step_38': {
                'checked': False,
            },
            #                 - new steps added -
            'step_39': {
                'checked': False,
            },
            'step_40': {
                'checked': False,
            },
            'step_42': {
                'non_cmv_property': 0,
            },
            'step_43': {
                'straight_trucks': {
                    'owned': 1,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'truck_tractors': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'trailers': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'iep_trailer_chassis_only': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                    'serviced': 0,
                },
            },
            'step_44': {
                # 'canada': 0,
                # 'mexico': 0,
                'non_cmv_property': 0,
            },
            'step_45': {
                # 'questionCode_B0061P060081S06008_Q06048_id': 0,
                'straight_trucks': {
                    'owned': 1,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'truck_tractors': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'trailers': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                },
                'iep_trailer_chassis_only': {
                    'owned': 0,
                    'term_leased': 0,
                    'trip_leased': 0,
                    'tow_driveway': 0,
                    'serviced': 0,
                },
            },
            'step_46': {
                # 'questionCode_B0061P060091S06009_Q06049_id': 1,
                'canada': 0,
                'mexico': 0,
            },
            #                 - New Steps Added
            'step_47': {
                'questionCode_B0061P060081S06008_Q06048_id': 1,
            },
            'step_48': {
                'questionCode_B0061P060091S06009_Q06049_id': 0,
            },
            'step_49': {
                'questionCode_B0071P070021S07002_Q07001_id': 0,
                'questionCode_B0071P070021S07002_Q07002_id': 0,
            },
            'step_50': {
                'questionCode_B0071P070051S07003_Q07003_id': 1,
                'questionCode_B0071P070051S07003_Q07004_id': 0,
            },
            'step_51': {
                'questionCode_B0071P070061S07004_Q07005_id': 0,
            },
            'step_52': {
                # 'canada': 0,
                # 'mexico': 0,
                'questionCode_B0071P070021S07002_Q07001_id': 1,
                'questionCode_B0071P070021S07002_Q07002_id': 0,
            },
            'step_53': {
                'questionCode_B0071P070051S07003_Q07003_id': 0,
                'questionCode_B0071P070051S07003_Q07004_id': 0,
            },
            'step_55': {
                'checked': True,
            },
            'step_56': {
                'questionCode_B0071P070061S07004_Q07005_id': 0,
            },
            'step_57': {
                'canada': 0,
                'mexico': 0,
            },
            'step_58': {
                'checked': False,
            },
            'step_61': {
                # 'first_name': first_name,
                # 'last_name': last_name,
                # 'esignature_application_password': password,
                # 'title': 'owner',
                'checked': False,
            },
            'step_64': {
                'first_name': first_name,
                'last_name': last_name,
                'esignature_application_password': password,
                'title': 'owner',
            },
            'step_69': {
                'electronic_signature_application_password': password,
            },
            'step_72': {
                'first_name': first_name,
                'last_name': last_name,
                'esignature_application_password': password,
                'title': 'owner',
            },
            'step_74': {
                'checked': True,
            },
            'step_75': {
                'user_id': email,
                'email': email,
                'password': password,
                # 'method_of_contact': 'Both',
                'method_of_contact': 'US Mail',
            },
            'step_76': {
                'checked': True,
            },
            'step_78': {
                'first_name': first_name,
                'last_name': last_name,
                'title': 'owner',
                'checked': True,
            },
            'step_80': {
                'first_name': first_name,
                'last_name': last_name,
                'title': 'owner',
                'checked': True,
            },
            'step_83':{}
        }
    else:
        data = {
            "step_9": {
                "create_password": password,
                "confirm_password": password,
                "security_question_1": "What was my high school mascot?",
                "security_answer_1": "bear",
                "security_question_2": "What is the make of my first car?",
                "security_answer_2": "ford",
                "security_question_3": "What is my pet name?",
                "security_answer_3": "baby",
            },
            "step_11": {
                "application_contact_type": "Applicant Representative",
                "application_contact_first_name": first_name,
                "application_contact_last_name": last_name,
                "application_contact_title": "owner",
                "application_contact_country": country,
                "application_contact_street_address_line_1": address,
                "application_contact_postal_code": postal_code,
                "application_contact_telephone_number": {
                    "country_code": country,
                    "area_code": area_code,
                    "phone_number": phone_number_fake,
                    "extra_phone_number": "",
                },
                "application_contact_email_address": email_fake,
                "application_contact_confirm_email_address": email_fake,
                "application_contact_preferred_contact_method": "US Mail",
            },
            "step_13": {
                "checked": False,
            },
            "step_14": {
                "legal_business_name": company_name,
            },
            "step_16": {
                "checked": True,
            },
            "step_17": {
                "mailing_address_sameas_principal": True,
            },
            "step_18": {
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_19": {},
            "step_20": {
                "checked": False,
            },
            "step_21": {
                "checked": "Limited Liability Company",
                "choose_one": state.upper(),
            },
            "step_22": {
                "checked": "Owned/controlled by citizen of United States",
            },
            "step_23": {
                "company_contact_1_checked": True,
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "email": email,
                "country": country,
                "area_code": area_code,
                "phone_number": phone_number_fake,
            },
            "step_24": {
                "country": country,
                "street_address_or_route_number_line_1": address,
                "postal_code": postal_code,
                "blank_click": True,
            },
            "step_27": {
                "checked": False,
            },
            "step_28": {
                "checked": True,
            },
            "step_29": {
                "checked": True,
            },
            "step_31": {
                "checked": False,
            },
            "step_32": {
                "checked": False,
            },
            "step_33": {
                "checked": False,
            },
            "step_34": {
                "checked": False,
            },
            "step_35": {
                "checked": False,
            },
            "step_36": {
                "checked": False,
            },
            "step_37": {
                "checked": False,
            },
            "step_38": {
                "checked": False,
            },
            "step_42": {
                "non_cmv_property": 0,
            },
            "step_43": {
                "straight_trucks": {
                    "owned": 1,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "truck_tractors": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "trailers": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                },
                "iep_trailer_chassis_only": {
                    "owned": 0,
                    "term_leased": 0,
                    "trip_leased": 0,
                    "tow_driveway": 0,
                    "serviced": 0,
                },
            },
            "step_44": {
                "canada": 0,
                "mexico": 0,
            },
            "step_45": {
                "questionCode_B0061P060081S06008_Q06048_id": 0,
            },
            "step_46": {
                "questionCode_B0061P060091S06009_Q06049_id": 1,
            },
            "step_49": {
                "questionCode_B0071P070021S07002_Q07001_id": 0,
                "questionCode_B0071P070021S07002_Q07002_id": 0,
            },
            "step_50": {
                "questionCode_B0071P070051S07003_Q07003_id": 1,
                "questionCode_B0071P070051S07003_Q07004_id": 0,
            },
            "step_51": {
                "questionCode_B0071P070061S07004_Q07005_id": 0,
            },
            "step_52": {
                "canada": 0,
                "mexico": 0,
            },
            "step_55": {
                "checked": True,
            },
            "step_58": {
                "checked": False,
            },
            "step_61": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_69": {
                "electronic_signature_application_password": password,
            },
            "step_72": {
                "first_name": first_name,
                "last_name": last_name,
                "esignature_application_password": password,
                "title": "owner",
            },
            "step_74": {
                "checked": True,
            },
            "step_75": {
                "user_id": email,
                "email": email,
                "password": password,
                "method_of_contact": "Both",
            },
            "step_76": {
                "checked": True,
            },
            "step_78": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_80": {
                "first_name": first_name,
                "last_name": last_name,
                "title": "owner",
                "checked": True,
            },
            "step_83": {},
        }

    if ein:
        data["step_19"]["ein"] = str(ein).replace("-", "")
    elif ssn:
        data["step_19"]["ssn"] = str(ssn).replace("-", "")

    if is_automate_paid:
        data["step_83"] = initial_data.get("paid", {})

    return data
