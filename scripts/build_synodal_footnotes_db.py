import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS_DIR = os.path.join(BASE_DIR, 'Data', 'Service Books', 'Typikon', 'readable_parts')
FOOTNOTES_PATH = os.path.join(PARTS_DIR, 'Final_footnotes.txt')
OUTPUT_PATH = os.path.join(BASE_DIR, 'json_db', 'synodal_footnotes.json')

PARTS = {
    'intro': os.path.join(PARTS_DIR, 'Final_Dolnytsky_intro.txt'),
    'part_1_structure': os.path.join(PARTS_DIR, 'Final_Dolnytsky_part1_structure.txt'),
    'part_2_general_rubrics': os.path.join(PARTS_DIR, 'Final_Dolnytsky_part2_general_rubrics.txt'),
    'part_3_menaion': os.path.join(PARTS_DIR, 'Final_Dolnytsky_part3_menaion.txt'),
    'part_4_triodion': os.path.join(PARTS_DIR, 'Final_Dolnytsky_part4_triodion.txt'),
    'part_5_temple': os.path.join(PARTS_DIR, 'Final_Dolnytsky_part5_temple.txt'),
    'appendix': os.path.join(PARTS_DIR, 'Final_Dolnytsky_appendix.txt')
}

def extract_anchors():
    anchors = {}
    for part_id, path in PARTS.items():
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        current_section = ''
        current_service = ''
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            upper = stripped.upper()
            if 'VESPERS' in upper:
                current_service = 'Vespers'
            elif 'MATINS' in upper:
                current_service = 'Matins'
            elif 'LITURGY' in upper or 'TYPIKA' in upper:
                current_service = 'Liturgy'
            elif 'COMPLINE' in upper:
                current_service = 'Compline'
            elif 'MIDNIGHT OFFICE' in upper:
                current_service = 'Midnight Office'
            elif 'HOUR' in upper:
                current_service = 'Hours'
            if stripped.startswith('#') or stripped.startswith('•') or stripped.startswith('o') or (stripped.isupper() and len(stripped) < 60):
                current_section = stripped.lstrip('#•o ').strip()
            for m in re.finditer(r'\[\^([^\]]+)\]', line):
                fn_id = m.group(1).strip()
                start = max(0, m.start() - 150)
                end = min(len(line), m.end() + 150)
                snippet = line[start:end].strip()
                if fn_id not in anchors:
                    anchors[fn_id] = []
                anchors[fn_id].append({
                    'part': part_id,
                    'section': current_section,
                    'service': current_service,
                    'anchor_snippet': snippet
                })
    return anchors

def classify_footnote(fn_id, text, anchors):
    text_lower = text.lower()
    combined_ctx = text_lower + ' ' + ' '.join([a.get('section', '').lower() + ' ' + a.get('anchor_snippet', '').lower() for a in anchors])
    services = []
    if any(k in combined_ctx for k in ['vespers', 'lord, i have cried', 'aposticha', 'litiya', 'gladsome light', 'lamp-lighting']):
        services.append('Vespers')
    if any(k in combined_ctx for k in ['matins', 'six psalms', 'polyeleos', 'praises', 'sessional hymn', 'god is the lord', 'evlogitaria']):
        services.append('Matins')
    if any(k in combined_ctx for k in ['liturgy', 'typika', 'antiphon', 'beatitudes', 'prokeimenon', 'epistle', 'gospel', 'cherubic', 'zadostoinyk', 'communion hymn']):
        services.append('Liturgy')
    if any(k in combined_ctx for k in ['compline', 'great compline', 'small compline']):
        services.append('Compline')
    if any(k in combined_ctx for k in ['midnight office']):
        services.append('Midnight Office')
    if any(k in combined_ctx for k in ['hour', 'royal hours', 'first hour', 'third hour', 'sixth hour', 'ninth hour']):
        services.append('Hours')
    for a in anchors:
        srv = a.get('service')
        if srv and srv not in services:
            services.append(srv)
    if not services:
        services = ['General']

    tags = []
    tag_map = {
        'censing': ['censer', 'cense', 'censing', 'incense', 'thymiama'],
        'vestments': ['vesting', 'vestment', 'phelonion', 'epitrachelion', 'orarion', 'dalmatic', 'robes'],
        'litanies': ['litany', 'litanies', 'small litany', 'in peace', 'let us say', 'let us complete'],
        'kathismata': ['kathisma', 'kathismata', 'psalm 118', 'sessional', 'stichology'],
        'canons': ['canon', 'canons', 'heirmos', 'heirmoi', 'ode', 'katavasia', 'irmos'],
        'readings': ['paremia', 'paremias', 'epistle', 'gospel', 'apostle', 'readings', 'prophecy'],
        'antiphons': ['antiphon', 'antiphons', 'beatitudes', 'it is good'],
        'troparia': ['troparion', 'troparia', 'kontakion', 'kontakia', 'hypakoe', 'exapostilarion', 'theotokion'],
        'prostrations': ['bow', 'bows', 'prostration', 'prostrations', 'kneel', 'kneeling', 'earth'],
        'fasting': ['fast', 'fasting', 'abstinence', 'oil', 'wine', 'meatfare', 'cheesefare']
    }
    for tag, kws in tag_map.items():
        if any(kw in combined_ctx for kw in kws):
            tags.append(tag)

    is_parish = any(w in text_lower for w in ['parish', 'parishes', 'custom', 'customs', 'local custom', 'our churches', 'our simple people', 'with us'])
    is_academic = any(w in text_lower for w in ['glagolitic', 'vatican', 'century', 'manuscript', 'in the translation', 'corrected by me', 'ivan dutka', 'appendix', 'title of the original', 'propaganda 1876', 'edition']) and not any(w in text_lower for w in ['prescribes', 'taken', 'sung', 'said', 'censing', 'troparion', 'litany'])
    
    if is_parish:
        category = 'parish_custom'
    elif is_academic:
        category = 'historical_apparatus'
    else:
        category = 'rubric_alternative'

    triggers = {}
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    date_matches = []
    for month_name, m_num in months.items():
        for m in re.finditer(rf'{month_name}\s+(\d{{1,2}})', text_lower):
            d_num = int(m.group(1))
            date_matches.append(f'menaion.{m_num}{d_num:02d}')
        for m in re.finditer(rf'(\d{{1,2}})\s+{month_name}', text_lower):
            d_num = int(m.group(1))
            date_matches.append(f'menaion.{m_num}{d_num:02d}')
    if date_matches:
        triggers['menaion_keys'] = sorted(list(set(date_matches)))

    if 'great lent' in text_lower or 'great forty days' in text_lower or 'cheesefare' in text_lower:
        triggers['season'] = 'triodion'
    elif 'bright week' in text_lower or 'pascha' in text_lower:
        triggers['season'] = 'pascha'
    elif 'pentecost' in text_lower:
        triggers['season'] = 'pentecostarion'

    component_triggers = []
    if 'censing' in tags and ('deacon' in text_lower or 'two deacons' in text_lower):
        component_triggers.append('censing_initial')
    if 'kathismata' in tags and 'litany' in text_lower:
        component_triggers.append('kathismata_litanies')
    if 'antiphons' in tags and ('typika' in text_lower or 'it is good' in text_lower):
        component_triggers.append('liturgy_antiphons')
    if 'troparia' in tags and 'polyeleos' in text_lower:
        component_triggers.append('polyeleos_troparia')
    if component_triggers:
        triggers['components'] = component_triggers

    return category, services, tags, triggers

def build_footnotes_database():
    print(f'Reading footnotes from {FOOTNOTES_PATH}...')
    with open(FOOTNOTES_PATH, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    pattern = re.compile(r'\[\^([^\]]+)\]:\s*(.*?)(?=\n\[\^|\Z)', re.DOTALL)
    raw_footnotes = pattern.findall(raw_text)
    print(f'Found {len(raw_footnotes)} raw footnotes.')
    print('Extracting anchor contexts across all Typikon parts...')
    anchors_map = extract_anchors()
    db = {}
    for fn_id, raw_content in raw_footnotes:
        fn_id_clean = fn_id.strip()
        content_clean = raw_content.strip()
        anchors = anchors_map.get(fn_id_clean, [])
        category, services, tags, triggers = classify_footnote(fn_id_clean, content_clean, anchors)
        primary_part = anchors[0]['part'] if anchors else 'unknown'
        primary_section = anchors[0]['section'] if anchors else ''
        db[fn_id_clean] = {
            'id': f'footnote_{fn_id_clean}',
            'number': fn_id_clean,
            'text': content_clean,
            'category': category,
            'authority': 'Dolnytsky Typikon (1891 Synod of Lviv)',
            'typikon_part': primary_part,
            'section': primary_section,
            'services': services,
            'tags': tags,
            'triggers': triggers,
            'anchors': anchors
        }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_f:
        json.dump(db, out_f, ensure_ascii=False, indent=2)
    print(f'Successfully generated {OUTPUT_PATH} with {len(db)} structured footnotes!')
    return db

if __name__ == '__main__':
    build_footnotes_database()