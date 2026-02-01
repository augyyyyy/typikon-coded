# Typikon In-Depth Search Methodology

> **Purpose**: Enable model replication of the Dolnytsky Typikon research process
> **Created**: 2026-01-31

---

## The 7-Step In-Depth Search Process

### Step 1: Locate the Relevant Section Header

**Goal**: Find the exact line where the service order is defined

**Method**: Use `grep_search` with the section title
```
grep_search(
  Query: "ORDER OF DAILY MATINS",
  Includes: ["dolnytsky_part*.txt"],
  SearchPath: "Data/Service Books/Typikon"
)
```

**Output**: Returns the line number (e.g., Line 203 in dolnytsky_part1_structure.txt)

---

### Step 2: Read the Full Section

**Goal**: Extract ALL elements in order, not just keywords

**Method**: Use `view_file` with a generous range (50-100 lines after the header)
```
view_file(
  AbsolutePath: "dolnytsky_part1_structure.txt",
  StartLine: 200,
  EndLine: 280  # Generous range to capture full section
)
```

**Critical**: Read the ENTIRE block, not just the first paragraph. Many key elements are in continuation text.

---

### Step 3: Extract Element-by-Element

**Goal**: Create a sequential list of every liturgical element mentioned

**Method**: Parse the Typikon text manually, extracting:
- Explicit element names (e.g., "Sessional Hymn")
- Implicit elements (e.g., "everything happens just as at Great Matins")
- Conditional elements (e.g., "except for the Katavasia, which will not be...")
- Refrains and responses

**Example extraction from Line 204**:
```
1. "From beginning...to second Sessional Hymn" → SAME AS GREAT
2. "After second Sessional Hymn...50th Psalm" → PSALM 50
3. "immediately the Canon" → CANON
4. "Katavasia...only after 3rd, 6th, 8th, 9th" → KATAVASIA PATTERN
5. "After the Canon – 'It is truly meet'" → IT IS TRULY MEET
6. "after the Exaposteilarion" → EXAPOSTILARION
7. "Psalms of the Praises, simply, without singing" → PRAISES (READ)
8. "Small Doxology is read" → SMALL DOXOLOGY
...etc
```

---

### Step 4: Cross-Reference with Related Sections

**Goal**: Find additional rules that modify the base structure

**Method A**: Search for variant-specific keywords
```
grep_search(
  Query: "Lenten Matins",
  Includes: ["*.txt"],
  SearchPath: "Data/Service Books/Typikon"
)
```

**Method B**: Search for specific elements that might have additional rules
```
grep_search(
  Query: "two saints",
  SearchPath: "Data/Service Books/Typikon"  # For stacking rules
)
```

**Method C**: View footnotes that clarify ambiguous elements
```
view_file(
  AbsolutePath: "footnotes.txt",
  StartLine: <relevant_footnote_range>
)
```

---

### Step 5: View the Current Implementation

**Goal**: Compare Typikon requirements against existing JSON

**Method**: View the current struct file
```
view_file(
  AbsolutePath: "01i_struct_matins.json",
  StartLine: 482,  # daily_matins section
  EndLine: 600
)
```

**Also**: Search for all function hooks in the JSON
```
grep_search(
  Query: "\"function\":",
  Includes: ["01i_struct_matins.json"],
  SearchPath: "json_db"
)
```

---

### Step 6: Create Element Comparison Matrix

**Goal**: Side-by-side gap identification

**Method**: Build a table with columns:
| Element | Typikon Requirement | Current Implementation | Gap? | Citation |

For each row:
- ✅ = Implemented correctly
- ⚠️ = Partially implemented
- ❌ = Missing entirely

---

### Step 7: Verify Gaps Are TRUE Gaps

**Goal**: Eliminate false positives

**Method A**: Check if "missing" element exists in components
```
grep_search(
  Query: "element_name",
  Includes: ["00_components.json"],
  SearchPath: "json_db"
)
```

**Method B**: Check if element is definitional (no resolve needed)
- Example: "Small Doxology" is ALWAYS small in Daily Matins — no resolve needed

**Method C**: Check if Typikon explicitly says element is ABSENT
- Example: "Small Litanies...are refused at Small Matins" → NOT a gap

---

## Key Patterns for Typikon Research

### Pattern 1: "Same As" References
When text says "everything...as at Great Matins", you must:
1. Identify exactly WHERE the "same as" ends
2. Look for the "with the exception of" clause
3. Parse what comes AFTER the exception

### Pattern 2: Numbered Rubrics
Typikon often uses numbered lists (1., 2., 3.) for order-dependent elements. Extract EVERY number.

### Pattern 3: Conditional Language
Watch for:
- "if there be" → Optional element
- "except when" → Suppression rule
- "in the Fore- and Afterfeast" → Seasonal override

### Pattern 4: Footnote References
Superscript numbers (e.g., ^[77]) point to `footnotes.txt` with critical clarifications.

---

## Files to Always Check

| File | Content | When to Check |
|:-----|:--------|:--------------|
| `dolnytsky_part1_structure.txt` | Base service orders | Always first |
| `dolnytsky_part2_general_rubrics.txt` | 20 paradigms, stacking rules | Saints combinations |
| `dolnytsky_part4_triodion.txt` | Lenten/Paschal variations | Lenten services |
| `footnotes.txt` | Clarifications, exceptions | When ambiguous |

---

## Example: Complete Search for "Daily Matins"

```
# Step 1: Locate
grep_search(Query="ORDER OF DAILY MATINS", Includes=["dolnytsky_part1*.txt"])
→ Found: Line 203

# Step 2: Read full section
view_file(dolnytsky_part1_structure.txt, StartLine=200, EndLine=220)
→ Full text of Line 204 extracted

# Step 3: Extract elements (manual parsing)
→ 15 elements identified from the text

# Step 4: Cross-reference
grep_search(Query="Small Doxology")
→ Found 25 references confirming rules

# Step 5: View implementation
view_file(01i_struct_matins.json, StartLine=482, EndLine=600)
→ Found 5 hooks currently implemented

# Step 6: Build matrix
→ 15 Typikon elements vs 5 implemented = 10 potential gaps

# Step 7: Verify gaps
→ 5 TRUE gaps after ruling out definitional and component-based elements
```

---

## Common Mistakes to Avoid

1. **Quick scanning** - Reading only first paragraph misses continuation text
2. **Ignoring footnotes** - Critical rules often in footnotes, not main text
3. **Assuming gaps** - Many elements exist in `00_components.json`, not struct files
4. **Missing conditionals** - "except", "unless", "if" clauses define real behavior
5. **Ignoring inheritance** - Lenten inherits from Daily, which inherits from Great
