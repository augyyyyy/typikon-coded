
import json
import os
import sys
from ruthenian_engine import RuthenianEngine
from datetime import date

def generate_encyclopedia(date_str, temple_patron, version="stamford_2014"):
    print(f"\n=== CODING THE TYPIKON: ENCYCLOPEDIA GENERATOR ===")
    print(f"Date: {date_str}")
    print(f"Temple Patron: {temple_patron}")
    print(f"Recension ID: {version}")
    print("==================================================\n")

    # Initialize Engine
    base_dir = os.path.dirname(os.path.abspath(__file__))
    engine = RuthenianEngine(base_dir=base_dir, version=version)
    
    # Mock Context
    # In real app, this comes from calendar date object
    d = date.fromisoformat(date_str)
    context = engine.get_liturgical_context(d)
    context["temple_patron"] = temple_patron
    
    # 1. VISUALIZER: PARADIGM IDENTIFICATION
    paradigm = engine.identify_paradigm(context)
    print(f"[LOGIC GATE: Dolnytsky §II] -> Paradigm Identified: [{paradigm}]")
    print("-" * 50)

    # SEQUENCE OF SERVICES
    services = ["vespers", "compline", "midnight", "matins", "hours", "typika"]

    for service_name in services:
        print_service_header(service_name)
        print_service_map(service_name)
        
        if service_name == "vespers":
            render_vespers(engine, context)
        elif service_name == "compline":
            render_compline(engine, context)
        elif service_name == "midnight":
            render_midnight(engine, context)
        elif service_name == "matins":
            render_matins(engine, context)
        elif service_name == "hours":
            render_hours(engine, context)
        elif service_name == "typika":
            render_typika(engine, context)

def print_service_header(name):
    print(f"\n{'#'*40}")
    print(f"# {name.upper()}")
    print(f"{'#'*40}\n")

def print_service_map(name):
    print(f"[SERVICE MAP: {name.upper()}]")
    if name == "vespers":
        print("Enarxis -> Kathisma -> Lamp-Lighting -> Entrance -> Prokimenon -> Readings -> Lity -> Aposticha -> Dismissal")
    elif name == "matins":
        print("Royal Office -> Hexapsalmos -> God is the Lord -> Kathismata -> Polyeleos -> Gospel -> Canon -> Praises -> Doxology")
    print("-" * 20)

def render_vespers(engine, context):
    # Resolve Fixed Texts
    psalm_103 = engine.get_text("psalm_103", logic_requirement="Enarxis Structure")
    print(f"\n[Psalm 103]: {psalm_103['content'][:50]}..." if psalm_103 and not psalm_103.get('is_missing') else f"{psalm_103['content']}")

    # Demonstrate Logic Gates
    print(f"\n[Entrance Logic]")
    print(f">>> Isodikon: {engine.resolve_isodikon(context)['verse']}")
    
    print(f"\n[Dismissal Construction]")
    dismissal = engine.construct_dismissal(context, temple_saint=context["temple_patron"])
    print(f">>> {dismissal}")

def render_compline(engine, context):
    comp = engine.get_text("compline_service", logic_requirement="Lenten/Vigil Requirement")
    if comp and not comp.get('is_missing'):
        print("[TEXT SOURCE: Stamford Horologion]")
        print(comp['content'][:100] + "...")
    else:
        print(comp['content'])

def render_midnight(engine, context):
    noct = engine.get_text("nocturn_service", logic_requirement="Daily Cycle Requirement")
    if noct and not noct.get('is_missing'):
        print("[TEXT SOURCE: Stamford Horologion]")
        print(noct['content'][:100] + "...")
    else:
        print(noct['content'])

def render_matins(engine, context):
    print(f"\n[Temple Priority Check]")
    stack = engine.resolve_temple_priority(context, temple_type="saint")
    print(f">>> Troparia Stack: {stack}")
    
    print(f"\n[Ode 9 Logic]")
    zad = engine.resolve_zadostoinyk(context)
    print(f">>> Refrain: {zad['content']}")

def render_hours(engine, context):
    hours = ["first_hour", "third_hour", "sixth_hour", "ninth_hour"]
    for h in hours:
        text = engine.get_text(f"prayer_{h}", logic_requirement=f"Structure of {h}")
        print(f"\n[{h.replace('_', ' ').title()}]")
        print(text['content'][:50] + "..." if text and not text.get('is_missing') else text['content'])

def render_typika(engine, context):
    print("\n[Divine Liturgy (Represented by Typika for Prototype)]")
    beat = engine.get_text("typika_beatitudes", logic_requirement="Typika Structure")
    print(f"\n[The Beatitudes]")
    print(beat['content'][:50] + "..." if beat and not beat.get('is_missing') else beat['content'])

if __name__ == "__main__":
    generate_encyclopedia("2025-04-27", "St. Nicholas", version="stamford_2014")
