import json

DB_FILE = r"E:\Google Antigravity\Projects\Typikon Coded\json_db\02a_logic_general.json"

with open(DB_FILE, "r", encoding="utf-8") as f:
    db = json.load(f)

def add_aposticha(case_id, distrib):
    if case_id in db:
        if 'variables' not in db[case_id]:
            db[case_id]['variables'] = {}
        db[case_id]['variables']['aposticha_distribution'] = distrib

add_aposticha('case_01_sunday_simple', {
    "source_ref": "Dolnytsky Part II Line 86",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "none",
    "both_now": "aposticha_theotokion"
})

add_aposticha('case_02_weekday_simple', {
    "source_ref": "Dolnytsky Part II Line 100",
    "total_count": 3,
    "distribution": [{"source": "octoechos", "type": "daily", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "aposticha_theotokion"
})

add_aposticha('case_03_weekday_6stichera', {
    "source_ref": "Dolnytsky Part II Line 135",
    "total_count": 3,
    "distribution": [{"source": "octoechos", "type": "daily", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "aposticha_theotokion"
})

add_aposticha('case_04_sunday_polyeleos', {
    "source_ref": "Dolnytsky Part II Line 170",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "saint_doxastikon",
    "both_now": "aposticha_theotokion"
})

add_aposticha('case_05_weekday_polyeleos', {
    "source_ref": "Dolnytsky Part II Line 196",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "saint", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "aposticha_theotokion"
})

add_aposticha('case_06_sunday_vigil', {
    "source_ref": "Dolnytsky Part II Line 226 — same as Polyeleos Sunday",
    "inherits": "CASE_04"
})

add_aposticha('case_07_weekday_vigil', {
    "source_ref": "Dolnytsky Part II Line 246 — same as Polyeleos Weekday",
    "inherits": "CASE_05"
})

add_aposticha('case_08_sunday_forefeast', {
    "source_ref": "Dolnytsky Part II Line 259",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "saint_doxastikon",
    "both_now": "forefeast_theotokion"
})

add_aposticha('case_09_weekday_forefeast', {
    "source_ref": "Dolnytsky Part II Line 288",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "forefeast", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "forefeast_theotokion"
})

add_aposticha('case_10_feast_lord', {
    "source_ref": "Dolnytsky Part II Line 319",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "feast", "qty": 3}],
    "glory": "feast_doxastikon",
    "both_now": "feast_theotokion"
})

add_aposticha('case_11_theotokos_sunday', {
    "source_ref": "Dolnytsky Part II Line 347",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "feast_doxastikon",
    "both_now": "feast_theotokion"
})

add_aposticha('case_12_theotokos_weekday', {
    "source_ref": "Dolnytsky Part II Line 364 — inherits Case 10",
    "inherits": "CASE_10"
})

add_aposticha('case_13_afterfeast_sunday_simple', {
    "source_ref": "Dolnytsky Part II Line 380",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "saint_doxastikon",
    "both_now": "afterfeast_theotokion"
})

add_aposticha('case_14_afterfeast_weekday_simple', {
    "source_ref": "Dolnytsky Part II Line 405",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "feast", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "afterfeast_theotokion"
})

add_aposticha('case_15_afterfeast_sunday_polyeleos', {
    "source_ref": "Dolnytsky Part II Line 437",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "saint_doxastikon",
    "both_now": "afterfeast_theotokion"
})

add_aposticha('case_16_afterfeast_weekday_polyeleos', {
    "source_ref": "Dolnytsky Part II Line 464",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "saint", "qty": 3}],
    "glory": "saint_doxastikon",
    "both_now": "afterfeast_theotokion"
})

add_aposticha('case_17_afterfeast_sunday_vigil', {
    "source_ref": "Dolnytsky Part II Line 490 — same as Polyeleos Afterfeast Sunday",
    "inherits": "CASE_15"
})

add_aposticha('case_18_afterfeast_weekday_vigil', {
    "source_ref": "Dolnytsky Part II Line 499 — same as Polyeleos Afterfeast Weekday",
    "inherits": "CASE_16"
})

add_aposticha('case_19_apodosis_sunday', {
    "source_ref": "Dolnytsky Part II Line 510",
    "total_count": 4,
    "distribution": [{"source": "octoechos", "type": "resurrection", "qty": 4}],
    "glory": "feast_doxastikon",
    "both_now": "feast_theotokion"
})

add_aposticha('case_20_apodosis_weekday', {
    "source_ref": "Dolnytsky Part II Line 536",
    "total_count": 3,
    "distribution": [{"source": "menaion", "type": "feast", "qty": 3}],
    "glory": "feast_doxastikon",
    "both_now": "feast_theotokion"
})

with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
