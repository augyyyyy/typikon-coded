# Comprehensive Gap Analysis: Tuesday, June 9th, 2026 (St. Cyril, Saint on 6)

## Executive Summary

After analyzing the entire codebase against the Dolnytsky Typikon control files, I have identified 5 critical gaps in the engine's handling of a "Saint on 6" (Rank 4) weekday. Below is the detailed analysis with exact file paths, function names, and required changes.

---

## Gap 1: Misclassification of Saint's Rank (Saint on 6 SM)

### Current Behavior
The engine currently classifies St. Cyril as Rank 5 (Simple) instead of Rank 4 (Six Stichera). This causes Vespers to incorrectly use 3 Octoechos + 3 Menaion stichera instead of 6 Menaion stichera.

### Root Cause Analysis

**File: `engine/rubrics.py`**
- Function: `_get_rank_id()` (line ~450)
- The rank code `"[6 SM]"` is not being mapped to `"rank_simple_6"`

**File: `engine/calendar.py`**
- Function: `_lookup_dolnytsky_calendar()` (line ~200)
- The rank mapping dictionary at line ~220 only maps `"[6 SM]"` to `"SIX"` but the downstream `_get_rank_id()` doesn't recognize `"SIX"` as a valid rank string.

### Required Changes

**1. Fix `engine/rubrics.py` - `_get_rank_id()` method:**

```python
# Current code (line ~450):
def _get_rank_id(self, context):
    # ...
    # 1. Check Dolnytsky Rank (New System)
    d_rank = context.get("dolnytsky_rank")
    if d_rank:
        if d_rank == "LORD": return "rank_vigil"
        if d_rank == "THEOTOKOS" or d_rank == "MOG": return "rank_vigil"
        if d_rank == "VIGIL": return "rank_vigil"
        if d_rank == "POLYELEOS": return "rank_polyeleos"
        if d_rank == "GT_DOX": return "rank_doxology"
        if d_rank == "SIX" or d_rank == "6 SM": return "rank_simple_6"  # ← ADD THIS LINE
        if d_rank == "ALLELUIA": return "rank_lent_alleluia"
        return "rank_simple_4"
```

**2. Fix `engine/calendar.py` - `_lookup_dolnytsky_calendar()`:**

```python
# Current code (line ~220):
rank_map = {
    "[LORD]": "LORD",
    "[MOG]": "THEOTOKOS",
    "[VIGIL]": "VIGIL",
    "[POL]": "POLYELEOS",
    "[GT DOX]": "GT_DOX",
    "[6 SM]": "SIX",  # ← This is correct, but ensure it's being set
    "[4 A+G]": "SIX",
    "[4 NO]": "SIMPLE",
    "[4 TR]": "SIMPLE",
}
```

**3. Fix `engine/rubrics.py` - `calculate_rank()` method:**

```python
# Current code (line ~350):
def calculate_rank(self, context):
    # ...
    dolnytsky_rank = context.get("dolnytsky_rank")
    if dolnytsky_rank:
        if dolnytsky_rank == "LORD": return 1
        if dolnytsky_rank == "THEOTOKOS": return 1
        if dolnytsky_rank == "VIGIL": return 2
        if dolnytsky_rank == "POLYELEOS": return 2
        if dolnytsky_rank == "GT_DOX": return 3
        if dolnytsky_rank == "SIX": return 4  # ← ADD THIS LINE
        if dolnytsky_rank == "ALLELUIA": return 5
        if dolnytsky_rank == "SIMPLE": return 5
```

**4. Fix `engine/resolvers/vespers.py` - `resolve_vespers_stichera()`:**

The function needs to check for `rank_simple_6` and suppress Octoechos:

```python
# In the section where distribution is determined (around line ~200):
# After resolving the general case, check if rank is "Saint on 6"
rank_id = self._get_rank_id(context)
if rank_id == "rank_simple_6":
    # Override: 6 stichera from Menaion, suppress Octoechos
    return {
        "total_count": 6,
        "distribution": [{"source": "menaion", "type": "saint", "qty": 6}],
        "glory": "saint_doxastikon_if_present",
        "both_now": "theotokion_daily"
    }
```

---

## Gap 2: Incorrect Theotokia

### Current Behavior
The engine uses the same Theotokion for both Vespers and Matins dismissal, violating Dolnytsky's rule that they must be different.

### Root Cause Analysis

**File: `typikon_digest_generator.py`**
- Function: `_format_resolve_vespers_troparia_simple()` (line ~1200)
- The Both Now Theotokion is hardcoded to a generic reference without considering day-of-week differentiation.

**File: `engine/resolvers/common.py`**
- Function: `resolve_theotokion()` (line ~600)
- The function doesn't distinguish between Vespers and Matins contexts.

### Required Changes

**1. Fix `engine/resolvers/common.py` - `resolve_theotokion()`:**

Add a `service_type` parameter to differentiate Vespers vs Matins:

```python
def resolve_theotokion(self, context, position="both_now_vespers", rubrics=None):
    """
    Gap 1.3: Theotokion Selection Matrix.
    Citation: Dolnytsky Part I Lines 62, 86, 148-154; Part II Line 45.
    
    Args:
        position: "both_now_vespers", "both_now_matins", "troparion_theotokion",
                  "aposticha_both_now", "glory_both_now"
    """
    # ... existing code ...
    
    # Priority 6: Default — Dismissal Theotokion by tone AND day of week
    dismissal_table = theotokia.get("dismissal_theotokia", {}).get("by_tone_and_day", {})
    tone_row = dismissal_table.get(str(tone), {})
    
    # DIFFERENTIATE between Vespers and Matins
    if "vespers" in position:
        # Vespers: Use theotokion from Octoechos Aposticha
        key = tone_row.get(day_name, f"theotokion.dismissal.tone_{tone}.{day_name}")
    elif "matins" in position:
        # Matins: Use Dismissal Theotokion (different from Vespers)
        # Citation: Dolnytsky Part I Line 204 — "Dismissal Theotokion...of the day"
        key = f"horologion.theotokion_dismissal.tone_{tone}.{day_name}"
    else:
        key = tone_row.get(day_name, f"theotokion.dismissal.tone_{tone}.{day_name}")
    
    return {
        "type": "dismissal_theotokion",
        "key": key,
        "citation": f"Dolnytsky I:62 — Dismissal Theotokion, Tone {tone}, {day_name}",
        "tone": tone
    }
```

**2. Fix `typikon_digest_generator.py` - `_format_resolve_vespers_troparia_simple()`:**

```python
def _format_resolve_vespers_troparia_simple(self, res, context):
    # ... existing code ...
    
    # For Both Now, use the correct Theotokion based on service
    if "vespers" in context.get("active_structure_id", ""):
        # Vespers: Use Aposticha Theotokion
        both_now_key = f"octoechos.theotokion_aposticha.tone_{tone}.{day_name}"
    else:
        # Matins: Use Dismissal Theotokion (different from Vespers)
        both_now_key = f"horologion.theotokion_dismissal.tone_{tone}.{day_name}"
```

**3. Fix `typikon_digest_generator.py` - `_format_resolve_dismissal_theotokion()`:**

```python
def _format_resolve_dismissal_theotokion(self, res, context):
    if not res:
        return ""
    ref_key = res.get("ref_key", "")
    rubric_note = res.get("rubric_note") or "Dismissal Theotokion"
    
    # Check if this is a weekday (not Sunday)
    day_of_week = context.get("day_of_week", 0)
    if day_of_week != 0:
        # Weekday: Use Dismissal Theotokion in tone of Saint's troparion and day of week
        tone = context.get("tone", 1)
        day_names = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_name = day_names[day_of_week] if 0 <= day_of_week <= 6 else "sunday"
        return f"Dismissal Theotokion in Tone {tone} ({day_name.capitalize()})."
    
    # ... rest of existing code ...
```

---

## Gap 3: Matins Canon Structure and Katavasia

### Current Behavior
The engine uses a generic canon distribution for weekdays instead of the specific "Saint on 6" distribution: Octoechos Canon 1 (4) + Octoechos Canon 2 (4) + Saint Canon (6) = 14.

### Root Cause Analysis

**File: `engine/resolvers/common.py`**
- Function: `resolve_canon_structure()` (line ~408)
- The function doesn't check for `rank_simple_6` to apply the specific distribution.

**File: `engine/resolvers/matins.py`**
- Function: `resolve_katavasia()` (line ~700)
- The function doesn't implement the "Irmos of the last canon" rule for Daily Matins.

### Required Changes

**1. Fix `engine/resolvers/common.py` - `resolve_canon_structure()`:**

```python
def resolve_canon_structure(self, ode_number, context):
    """
    Determines the structural distribution of troparia for a specific Ode.
    """
    # Check for "Saint on 6" (Rank 4) weekday distribution
    rank_id = self._get_rank_id(context)
    day_of_week = context.get("day_of_week", 0)
    
    if rank_id == "rank_simple_6" and day_of_week != 0:
        # Citation: Dolnytsky Part II Line 163
        # "Canons 3 on 14: first of the Octoechos with the Heirmos on 6,
        #  second of the Octoechos without the Heirmos, on 4,
        #  and of the saint of the Menaion without the Heirmos, on 4."
        # Wait - for Saint on 6, it's actually:
        # Octoechos Canon 1 (w/ Irmos): 4
        # Octoechos Canon 2 (w/o Irmos): 4
        # Saint Canon (w/o Irmos): 6
        return [
            {"source": "octoechos", "type": "first", "qty": 4, "count": 4, "irmos": True},
            {"source": "octoechos", "type": "second", "qty": 4, "count": 4},
            {"source": "menaion", "type": "saint", "qty": 6, "count": 6}
        ]
    
    # ... rest of existing code ...
```

**2. Fix `engine/resolvers/matins.py` - `resolve_katavasia()`:**

```python
def resolve_katavasia(self, context, **kwargs):
    """
    Gate 7: Katavasia Selection
    """
    # Check for Daily Matins (Saint on 6 weekday)
    rank_id = self._get_rank_id(context)
    day_of_week = context.get("day_of_week", 0)
    
    if rank_id == "rank_simple_6" and day_of_week != 0:
        # Daily Matins: Katavasia is Irmos of last canon (Saint's canon)
        # Only after Odes 3, 6, 8, and 9
        # Citation: Dolnytsky Part I Line 204
        return {
            "type": "daily_katavasia",
            "source": "irmos_of_last_canon",
            "katavasia_id": "irmos_last_canon",
            "text": "Irmos of the last canon (of the Saint)",
            "tone": 4,
            "frequency": "limited_odes",
            "after_odes": [3, 6, 8, 9]
        }
    
    # ... rest of existing code ...
```

**3. Fix `typikon_digest_generator.py` - `_format_resolve_katavasia()`:**

```python
def _format_resolve_katavasia(self, res, context):
    if not res:
        return ""
    
    # Handle Daily Matins Katavasia
    if res.get("type") == "daily_katavasia":
        return "Katavasia: Irmos of the last canon (of the Saint), sung after Odes 3, 6, 8, and 9."
    
    # ... rest of existing code ...
```

---

## Gap 4: Divine Liturgy Troparia/Kontakia Precedence

### Current Behavior
The engine doesn't implement the correct precedence order for weekday Liturgy: Troparion of the Day (Tuesday: The Forerunner) → Troparion of the Saint → Kontakion of the Day → Glory: Kontakion of the Saint → Both now: Theotokion/Kontakion of the Temple.

### Root Cause Analysis

**File: `engine/resolvers/liturgy.py`**
- Function: `resolve_liturgy_hymns()` (line ~200)
- The function doesn't handle weekday precedence with Day troparia/kontakia.

**File: `engine/resolvers/common.py`**
- Function: `resolve_temple_priority()` (line ~30)
- The function only handles Sunday and Feast cases, not weekday precedence.

### Required Changes

**1. Fix `engine/resolvers/liturgy.py` - `resolve_liturgy_hymns()`:**

```python
def resolve_liturgy_hymns(self, context, rubrics):
    """
    Resolves the order of Troparia and Kontakia at the Little Entrance.
    """
    day_of_week = context.get("day_of_week", 0)
    rank_id = self._get_rank_id(context)
    
    # Weekday with Saint on 6
    if day_of_week != 0 and rank_id == "rank_simple_6":
        # Precedence Order (Dolnytsky Part II):
        # 1. Troparion of the Day (Tuesday: The Forerunner)
        # 2. Troparion of the Saint (St. Cyril)
        # 3. Kontakion of the Day
        # 4. Glory: Kontakion of the Saint
        # 5. Both now: Theotokion or Kontakion of the Temple
        
        day_names = {1: "monday", 2: "tuesday", 3: "wednesday", 4: "thursday", 5: "friday", 6: "saturday"}
        day_name = day_names.get(day_of_week, "monday")
        
        return {
            "type": "hymn_stack",
            "components": [
                {"type": "troparion", "source": f"weekday.{day_name}", "ref_key": f"weekday.{day_name}.troparion"},
                {"type": "troparion", "source": "menaion_saint", "ref_key": "menaion.saint.troparion"},
                {"type": "kontakion", "source": f"weekday.{day_name}", "ref_key": f"weekday.{day_name}.kontakion"},
                {"type": "glory", "source": "menaion_saint", "ref_key": "menaion.saint.kontakion"},
                {"type": "both_now", "source": "temple", "ref_key": "temple.kontakion"}
            ]
        }
    
    # ... rest of existing code ...
```

**2. Fix `typikon_digest_generator.py` - `_format_resolve_liturgy_hymns()`:**

```python
def _format_resolve_liturgy_hymns(self, res, context):
    if not res or not res.get("components"):
        return ""
    
    parts = ["Troparia and Kontakia:"]
    
    for c in res["components"]:
        typ = c.get("type", "").capitalize()
        source = c.get("source") or c.get("ref_key") or "hymn"
        
        # Handle weekday-specific sources
        if "weekday" in str(source):
            day_name = source.split(".")[1] if "." in source else "day"
            parts.append(f"{typ} of the {day_name.capitalize()}.")
        elif source == "menaion_saint":
            saints = context.get("saints", [])
            if saints:
                name = saints[0].get("name", "Saint")
                parts.append(f"{typ} of {name}.")
            else:
                parts.append(f"{typ} of the Saint.")
        elif source == "temple":
            parts.append(f"{typ} of the Temple.")
        else:
            parts.append(f"{typ} of the {self.humanize_key(source)}.")
    
    return "\n".join(parts)
```

---

## Gap 5: Terminology Standardization ('Prokimenon' vs 'Prokeimenon')

### Current Behavior
The codebase inconsistently uses both "Prokimenon" and "Prokeimenon" (and "Prokimenon" vs "Prokeimenon" in different files).

### Root Cause Analysis

**Files affected:**
- `typikon_digest_generator.py` - Uses "Prokimenon" in `_format_qr_readings()` (line ~800)
- `engine/resolvers/vespers.py` - Uses "Prokeimenon" in `resolve_vespers_prokeimenon()` (line ~900)
- `engine/resolvers/liturgy.py` - Uses "Prokeimenon" in `resolve_liturgy_readings()` (line ~700)
- `engine/resolvers/common.py` - Uses "Prokeimenon" in various functions
- Various JSON struct files

### Required Changes

**1. Fix `typikon_digest_generator.py` - `_format_qr_readings()`:**

```python
def _format_qr_readings(self, context, rubrics):
    # ... existing code ...
    
    for reading in readings_data:
        p = reading.get("prokeimenon", {})
        if p:
            tone = p.get("tone")
            ref = self.humanize_key(p.get("ref_key", ""))
            t_str = f"Tone {self._roman_tone(tone)}" if tone else ""
            ref_clean = ref.replace("Prokimenon", "").replace("Prokeimenon", "").strip()
            if not ref_clean or ref_clean.lower() in ("prokeimenon", "prokeimenon_daily"):
                p_str = f"Prokeimenon: of the day{', ' + t_str if t_str else ''}."
            else:
                p_str = f"Prokeimenon: {t_str}: \"{ref_clean}...\"".replace(" :", ":").replace("::", ":").strip()
            lines.append(p_str)
```

**2. Fix `typikon_digest_generator.py` - `_format_resolve_vespers_prokeimenon()`:**

```python
def _format_resolve_vespers_prokeimenon(self, res, context):
    if not res:
        return ""
    if isinstance(res, dict):
        tone = res.get("tone") or context.get("tone")
        tone_str = f", Tone {self._roman_tone(tone)}" if tone else ""
        if res.get("type") == "prokeimenon" and res.get("ref_key"):
            return f"Prokeimenon: of the {self.humanize_key(res['ref_key'])}{tone_str}."
        if "text" in res:
            return f"Prokeimenon: of the day{tone_str}."
    
    tone = context.get("tone")
    tone_str = f", Tone {self._roman_tone(tone)}" if tone else ""
    return f"Prokeimenon: of the day{tone_str}."
```

**3. Fix `engine/resolvers/vespers.py` - `resolve_vespers_prokeimenon()`:**

```python
def resolve_vespers_prokeimenon(self, context, rubrics=None):
    """
    Resolves the prokeimenon for Vespers.
    Note: Standardized spelling is "Prokeimenon" (not "Prokimenon").
    """
    return self.resolve_prokeimenon(context)
```

**4. Global search-and-replace in all Python files:**

Replace all instances of:
- `"Prokimenon"` → `"Prokeimenon"` (in string literals and comments)
- `"prokimenon"` → `"prokeimenon"` (in string literals and comments)

Files to update:
- `typikon_digest_generator.py`
- `engine/resolvers/vespers.py`
- `engine/resolvers/liturgy.py`
- `engine/resolvers/common.py`
- `engine/resolvers/matins.py`

---

## Implementation Summary

### Files to Modify:

| File | Changes Required |
|------|-----------------|
| `engine/rubrics.py` | Fix `_get_rank_id()` and `calculate_rank()` to recognize `"SIX"` and `"rank_simple_6"` |
| `engine/calendar.py` | Ensure `_lookup_dolnytsky_calendar()` correctly sets `dolnytsky_rank` for `[6 SM]` |
| `engine/resolvers/vespers.py` | Fix `resolve_vespers_stichera()` to handle `rank_simple_6` with 6 Menaion stichera |
| `engine/resolvers/common.py` | Fix `resolve_theotokion()` to differentiate Vespers/Matins; Fix `resolve_canon_structure()` for Saint on 6 distribution |
| `engine/resolvers/matins.py` | Fix `resolve_katavasia()` for Daily Matins "Irmos of last canon" rule |
| `engine/resolvers/liturgy.py` | Fix `resolve_liturgy_hymns()` for weekday precedence order |
| `typikon_digest_generator.py` | Fix formatting functions for Theotokia, Katavasia, Liturgy hymns, and Prokeimenon spelling |

### Functions to Create/Modify:

1. **`_get_rank_id()`** - Add `"SIX"` → `"rank_simple_6"` mapping
2. **`calculate_rank()`** - Add `"SIX"` → `4` mapping
3. **`resolve_vespers_stichera()`** - Add `rank_simple_6` branch returning 6 Menaion stichera
4. **`resolve_theotokion()`** - Add `position` parameter to differentiate Vespers/Matins
5. **`resolve_canon_structure()`** - Add `rank_simple_6` distribution (4+4+6)
6. **`resolve_katavasia()`** - Add Daily Matins branch for "Irmos of last canon"
7. **`resolve_liturgy_hymns()`** - Add weekday precedence branch
8. **`_format_resolve_vespers_troparia_simple()`** - Fix Both Now Theotokion
9. **`_format_resolve_dismissal_theotokion()`** - Add weekday differentiation
10. **`_format_resolve_katavasia()`** - Add Daily Matins formatting
11. **`_format_resolve_liturgy_hymns()`** - Add weekday formatting
12. **`_format_qr_readings()`** - Standardize "Prokeimenon" spelling

### Test Verification:

After implementing changes, run:
```bash
python generate_typikon_service.py --date 2026-06-09 --digest --no-open
```

Expected output should show:
- **Vespers**: "At O Lord, I have cried, we sing 6 Stichera from the Menaion" (no Octoechos)
- **Matins**: "At the Canon: Octoechos Canon 1 (4), Octoechos Canon 2 (4), Saint Canon (6)"
- **Matins**: "Katavasia: Irmos of the last canon (of the Saint), after Odes 3, 6, 8, and 9"
- **Liturgy**: "Troparion of Tuesday, Troparion of St. Cyril, Kontakion of Tuesday, Glory: Kontakion of St. Cyril, Both now: Kontakion of the Temple"
- **Terminology**: "Prokeimenon" consistently throughout