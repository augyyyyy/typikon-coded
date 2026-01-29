# Liturgical Intelligence Engine

> **Coding the Typikon**: A Logic-First approach to generating accurate liturgical services according to the Dolnytsky Typikon and other traditions.

The **Liturgical Intelligence Engine** is a Python-based system designed to dynamically generate liturgical service texts (Vespers, Matins, Liturgy, etc.) by applying complex rubrical logic to a database of liturgical assets. Unlike static text repositories, this engine calculates the correct service order based on the date, rank of the day, and concurrent feasts, handling complex interactions between the Octoechos, Menaion, and Triodion/Pentecostarion.

## Key Features

- **Logic-First Architecture**: Rubrics drive the text generation. The system first resolves *what* should be said before fetching *how* it should be said.
- **Dolnytsky Typikon Implementation**: Core logic is based on the 20 Paradigms of the Dolnytsky Typikon (Part II).
- **Dynamic Text Construction**: Generates strict-service booklets ("The Common") or full-text user booklets.
- **Multi-Recension Support**: Capable of handling different textual traditions (Stamford, Gregorian, etc.) through a unique ID system.
- **Verification Suite**: Includes automated stress tests to ensure rubrical accuracy across the liturgical year.

## Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/augyyyyy/typikon-coded.git
    cd typikon-coded
    ```

2.  (Optional) Create a virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

### Usage

The core engine can be invoked via the `ruthenian_engine.py` script or through specific generation scripts.

#### generating a Service

To generate a specific service (e.g., Vespers for a specific date):

```python
from ruthenian_engine import RuthenianEngine
from datetime import date

# Initialize Engine
engine = RuthenianEngine(version="stamford_2014")

# Context for a specific date
target_date = date(2026, 1, 11) # Sunday after Theophany
context = engine.get_liturgical_context(target_date)

# Resolve Rubrics
rubrics = engine.resolve_rubrics(context)
print(f"Service: {rubrics['title']}")

# Generate Full Booklet
booklet = engine.generate_full_booklet(context, rubrics)
print(booklet)
```

## Project Structure

- `ruthenian_engine.py`: The core logic engine.
- `json_db/`: The database of logic and text assets.
    - `01_struct_*`: Service structures (e.g., "After Psalm 103, say Great Litany").
    - `02_logic_*`: Decision trees and rubrical rules (e.g., "If Sunday, use Tone X").
    - `source_*`: Text repositories (Octoechos, Menaion, etc.).
- `parsers/`: Scripts to ingest raw text into the JSON database.
- `tests/` & `verification_examples/`: Unit tests and generated booklets for verification.

## Documentation

For more detailed information, please refer to:

- [Architecture Guide](ARCHITECTURE.md): Deep dive into the Logic-First design and engine internals.
- [Dolnytsky Implementation](DOLNYTSKY_IMPLEMENTATION.md): **Strict Canonical Logic**. A detailed breakdown of the 20 Paradigms, Precedence Rules, and "Weighing of Feasts" implementation.
- [Data Structure](DATA_STRUCTURE.md): Explanation of the JSON database schema and asset management.
- [Contributing](CONTRIBUTING.md): How to contribute code or textual corrections.

## License

[License Information Here]
