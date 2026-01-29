# Contributing to the Liturgical Intelligence Engine

Thank you for your interest in improving the Liturgical Intelligence Engine! We welcome contributions from developers, liturgists, and translators.

## How to Contribute

### 1. Reporting Bugs
If you find a logic error (e.g., "The engine prescribed the wrong Tone for Sunday") or a textual error ("Typo in the Troparion"):

*   Open an **Issue** on GitHub.
*   Clearly state the **Date** and **Service** where the error occurred.
*   Cite the **Rule** (e.g., "Dolnytsky Pg 145 says...") if applicable.

### 2. Adding Texts
The project is always in need of more text assets (especially for the Menaion and Triodion).

1.  Fork the repository.
2.  Follow the [Data Structure Guide](DATA_STRUCTURE.md) to create valid JSON assets.
3.  Place them in the appropriate `assets/` subfolder.
4.  Submit a Pull Request.

### 3. Improving Logic
For developers wishing to improve the engine:

*   **Logic Modules**: Most rubric changes should happen in `json_db/02*.json`, not the Python code.
*   **Engine Core**: Changes to `ruthenian_engine.py` require passing the full Verification Suite.

## Style Guide

*   **Python**: Follow PEP 8.
*   **JSON**: Use 2-space indentation. Ensure all JSON is valid.
*   **Commit Messages**: Use descriptive imperatives (e.g., "Add St. Basil Troparion", "Fix Vespers Entrance Logic").

## License
By contributing, you agree that your code will be licensed under the same license as the project (MIT/Apache 2.0).
