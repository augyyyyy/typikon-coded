def parse_rank_integer(rank_val):
    """
    Safely parses rank representations (integers, floats, numeric strings, or taxonomic string codes)
    into standard integer ranks (1 = highest, 5 = lowest).
    
    Mapping:
    - 1: Great Feasts of Lord/Theotokos ("rank_vigil_lord", "LORD", "THEOTOKOS")
    - 2: Vigil / Polyeleos ("rank_vigil", "rank_polyeleos", "VIGIL", "POLYELEOS")
    - 3: Great Doxology ("rank_doxology", "GT_DOX")
    - 4: Six Stichera ("rank_simple_6", "SIX")
    - 5: Simple / Small ("rank_simple_4", "SIMPLE", "ALLELUIA")
    """
    if rank_val is None:
        return 5
    if isinstance(rank_val, int):
        return rank_val
    if isinstance(rank_val, float):
        return int(rank_val)
    
    # Try converting numeric strings
    try:
        return int(rank_val)
    except ValueError:
        pass
    
    # Normalize string
    rank_str = str(rank_val).strip().lower()
    
    if "lord" in rank_str or "theotokos" in rank_str:
        return 1
    if "vigil" in rank_str or "polyeleos" in rank_str:
        return 2
    if "doxology" in rank_str or "gt_dox" in rank_str or "dox" in rank_str:
        return 3
    if "simple_6" in rank_str or "six" in rank_str:
        return 4
    if "simple_4" in rank_str or "simple" in rank_str or "alleluia" in rank_str:
        return 5
        
    # Default fallback
    return 5
