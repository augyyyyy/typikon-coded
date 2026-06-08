import pytest
import random
from datetime import date, timedelta
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

@pytest.fixture(scope="module")
def engine():
    return RuthenianEngine(".")

def test_fuzz_general_dates(engine):
    """
    Property-based fuzz test generating digests for 500 random dates
    across a 200-year span (1950 to 2150) to ensure engine robustness,
    absence of unhandled Python exceptions, and correctness of digest output.
    """
    generator = TypikonDigestGenerator(engine)
    
    start_date = date(1950, 1, 1)
    end_date = date(2150, 12, 31)
    delta = end_date - start_date
    
    # Seed for reproducibility
    rng = random.Random(42)
    
    # Select 500 random days
    random_days = [start_date + timedelta(days=rng.randint(0, delta.days)) for _ in range(500)]
    
    for idx, target_date in enumerate(random_days):
        try:
            # 1. Liturgical Context
            ctx = engine.get_liturgical_context(target_date)
            
            # 2. Rubrics Resolution
            rubrics = engine.resolve_rubrics(ctx)
            
            # 3. Digest Generation
            digest = generator.generate(ctx, rubrics, mode="quick")
            
            # 4. Assertions
            assert digest is not None, f"Digest was None for date {target_date}"
            assert "[ERROR:" not in digest, f"Found [ERROR: in digest for date {target_date}:\n{digest}"
            assert "[RESOLVE ERROR" not in digest, f"Found [RESOLVE ERROR in digest for date {target_date}:\n{digest}"
            assert "{'" not in digest, f"Found raw dict output in digest for date {target_date}:\n{digest}"
            
        except Exception as e:
            pytest.fail(f"Exception raised on date {target_date}: {e!r}")
