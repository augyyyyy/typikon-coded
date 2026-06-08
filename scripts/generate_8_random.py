import random
import datetime
import os
from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator

def generate_random_dates():
    engine = RuthenianEngine()
    generator = TypikonDigestGenerator(engine)
    
    start_date = datetime.date(1976, 1, 1)
    end_date = datetime.date(2076, 12, 31)
    
    delta = end_date - start_date
    
    random.seed(42) # For reproducible random selection
    random_dates = []
    for _ in range(8):
        random_days = random.randrange(delta.days)
        random_dates.append(start_date + datetime.timedelta(days=random_days))
        
    out_dir = 'generated_digests/random_tests'
    os.makedirs(out_dir, exist_ok=True)
    
    print('Selected 8 Random Dates:')
    for date_obj in random_dates:
        print(f'- {date_obj}')
        
        ctx = engine.get_liturgical_context(date_obj)
        rubrics = engine.resolve_rubrics(ctx)
        digest = generator.generate_full_service(ctx, rubrics)
        
        filepath = os.path.join(out_dir, f'Digest_{date_obj}.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(digest)
            
    print(f'\nDigests generated in {out_dir}')

if __name__ == '__main__':
    generate_random_dates()
