import sys
import os
from datetime import datetime

# Adjust path to project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

def test_pascha_rubrics():
    print("Initializing Engine...")
    engine = RuthenianEngine("json_db")
    generator = TypikonDigestGenerator(engine)
    
    # Target: PASCHA 2026-04-05
    dt = datetime(2026, 4, 5)
    print(f"Generating Digest for {dt.strftime('%Y-%m-%d')} (Pascha)...")
    
    # Prepare Context & Rubrics
    context = engine.get_liturgical_context(dt.date())
    rubrics = engine.resolve_rubrics(context)
    
    # Generate
    digest = generator.generate(context, rubrics)
    
    # Analysis
    print("\n--- DIGEST ANALYSIS ---")
    
    has_basil = "VESPERAL LITURGY" in digest or "ST. BASIL" in digest
    has_paschal_hours = "PASCHAL HOURS" in digest
    has_paschal_nocturns = "PASCHAL NOCTURNS" in digest or "midnight_paschal_nocturns" in digest
    
    print(f"1. Vesperal Liturgy (Basil): {'YES' if has_basil else 'NO'}")
    print(f"2. Paschal Hours (Compline): {'YES' if has_paschal_hours else 'NO'}")
    
    # Save to File
    output_path = os.path.join("generated_digests", f"digest_{dt.strftime('%Y-%m-%d')}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(digest)
    print(f"\n[Saved Digest]: {output_path}")

    # Dump first 20 lines for inspection
    print("\n[Preview]")
    print("\n".join(digest.splitlines()[:30]))

if __name__ == "__main__":
    test_pascha_rubrics()
