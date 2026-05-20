import json

DB_FILE = r"E:\Google Antigravity\Projects\Typikon Coded\json_db\02a_logic_general.json"

with open(DB_FILE, "r", encoding="utf-8") as f:
    db = json.load(f)

def add_hours_liturgy(case_id, hours, liturgy):
    if case_id in db:
        if 'variables' not in db[case_id]:
            db[case_id]['variables'] = {}
        db[case_id]['variables']['hours_distribution'] = hours
        db[case_id]['variables']['liturgy_distribution'] = liturgy

add_hours_liturgy('case_01_sunday_simple', 
    {"troparion": "sunday", "kontakion": "sunday", "glory": "saint_if_doxastikon_else_none"},
    {"antiphons": "sunday", "entrance": "sunday", "troparia": ["sunday", "saint"], "kontakia": ["sunday_glory", "saint_bothnow_theotokion"], "readings": ["sunday"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_02_weekday_simple',
    {"troparion": "day", "kontakion": "day", "glory": "saint_if_doxastikon"},
    {"antiphons": "daily", "entrance": "daily", "troparia": ["day", "saint"], "kontakia": ["day_glory", "saint_bothnow_theotokion"], "readings": ["day"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_03_weekday_6stichera',
    {"troparion": "day", "kontakion": "day", "glory": "saint"},
    {"antiphons": "daily", "entrance": "daily", "troparia": ["day", "saint"], "kontakia": ["day_glory", "saint_bothnow_theotokion"], "readings": ["day", "saint_if_reads"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_04_sunday_polyeleos',
    {"troparion": "sunday", "glory": "saint", "kontakion": "alternating_sunday_saint"},
    {"antiphons": "sunday", "entrance": "sunday", "troparia": ["sunday", "saint"], "kontakia": ["sunday_glory_saint", "bothnow_theotokion"], "readings": ["sunday", "saint"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_05_weekday_polyeleos',
    {"troparion": "saint", "glory": "none", "kontakion": "saint"},
    {"antiphons": "daily", "entrance": "saint", "troparia": ["saint"], "kontakia": ["saint"], "readings": ["day", "saint"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_06_sunday_vigil',
    {"source_ref": "inherits_case_04", "inherits": "case_04_sunday_polyeleos"},
    {"source_ref": "inherits_case_04", "inherits": "case_04_sunday_polyeleos"}
)

add_hours_liturgy('case_07_weekday_vigil',
    {"source_ref": "inherits_case_05", "inherits": "case_05_weekday_polyeleos"},
    {"source_ref": "inherits_case_05", "inherits": "case_05_weekday_polyeleos"}
)

add_hours_liturgy('case_08_sunday_forefeast',
    {"troparion": "sunday", "glory": "forefeast_and_saint_alternating", "kontakion": "alternating_forefeast_sunday"},
    {"antiphons": "sunday", "entrance": "sunday", "troparia": ["sunday", "forefeast"], "kontakia": ["sunday_bothnow_forefeast"], "readings": ["sunday"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_09_weekday_forefeast',
    {"troparion": "forefeast", "glory": "saint", "kontakion": "alternating_forefeast_saint"},
    {"antiphons": "daily", "entrance": "daily", "troparia": ["forefeast"], "kontakia": ["forefeast"], "readings": ["day"], "megalynarion": "it_is_truly_meet"}
)

add_hours_liturgy('case_10_feast_lord',
    {"troparion": "feast", "kontakion": "feast", "glory": "none"},
    {"antiphons": "feast", "entrance": "feast", "troparia": ["feast"], "kontakia": ["feast"], "readings": ["feast"], "megalynarion": "feast_irmos_9"}
)

add_hours_liturgy('case_11_theotokos_sunday',
    {"troparion": "sunday", "glory": "feast", "kontakion": "alternating_sunday_feast"},
    {"antiphons": "sunday", "entrance": "sunday_plus_theotokos_refrain", "troparia": ["sunday", "feast"], "kontakia": ["sunday_bothnow_feast"], "readings": ["sunday", "feast"], "megalynarion": "feast_irmos_9"}
)

add_hours_liturgy('case_12_theotokos_weekday',
    {"troparion": "feast", "kontakion": "feast", "glory": "none"},
    {"antiphons": "daily", "entrance": "normal_come", "troparia": ["feast"], "kontakia": ["feast"], "readings": ["feast"], "megalynarion": "feast_irmos_9"}
)

add_hours_liturgy('case_13_afterfeast_sunday_simple',
    {"troparion": "sunday", "glory": "alternating_feast_saint", "kontakion": "alternating_feast_sunday"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["sunday", "feast"], "kontakia": ["sunday_bothnow_feast"], "readings": ["sunday"], "megalynarion": "feast_irmos_9_if_lord"}
)

add_hours_liturgy('case_14_afterfeast_weekday_simple',
    {"troparion": "feast", "glory": "saint", "kontakion": "alternating_feast_saint"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["feast"], "kontakia": ["feast"], "readings": ["day_ap_gos_feast_prok"], "megalynarion": "feast_irmos_9"}
)

add_hours_liturgy('case_15_afterfeast_sunday_polyeleos',
    {"troparion": "sunday", "glory": "alternating_feast_saint", "kontakion": "threeway_sunday_feast_saint"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["sunday", "feast", "saint"], "kontakia": ["sunday_glory_saint_bothnow_feast"], "readings": ["sunday", "saint"], "megalynarion": "feast_irmos_9_if_lord"}
)

add_hours_liturgy('case_16_afterfeast_weekday_polyeleos',
    {"troparion": "feast", "glory": "saint", "kontakion": "alternating_feast_saint"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["feast", "saint"], "kontakia": ["saint_bothnow_feast"], "readings": ["day", "saint"], "megalynarion": "feast_irmos_9"}
)

add_hours_liturgy('case_17_afterfeast_sunday_vigil',
    {"source_ref": "inherits_case_15", "inherits": "case_15_afterfeast_sunday_polyeleos"},
    {"source_ref": "inherits_case_15", "inherits": "case_15_afterfeast_sunday_polyeleos"}
)

add_hours_liturgy('case_18_afterfeast_weekday_vigil',
    {"source_ref": "inherits_case_16", "inherits": "case_16_afterfeast_weekday_polyeleos"},
    {"source_ref": "inherits_case_16", "inherits": "case_16_afterfeast_weekday_polyeleos"}
)

add_hours_liturgy('case_19_apodosis_sunday',
    {"troparion": "sunday", "glory": "feast", "kontakion": "alternating_sunday_feast"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["sunday", "feast"], "kontakia": ["sunday_bothnow_feast"], "readings": ["sunday_only_if_lord", "sunday_plus_feast_if_theotokos"], "megalynarion": "feast_irmos_9_if_lord"}
)

add_hours_liturgy('case_20_apodosis_weekday',
    {"troparion": "feast", "glory": "none", "kontakion": "feast_only"},
    {"antiphons": "afterfeast", "entrance": "afterfeast", "troparia": ["feast"], "kontakia": ["feast"], "readings": ["day_if_lord", "day_plus_feast_if_theotokos"], "megalynarion": "feast_irmos_9"}
)

with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
