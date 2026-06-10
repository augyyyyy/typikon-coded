# Cantor Dashboard — GUI Features Roadmap & Architecture Spec
**Authoritative Architectural & Visual Interface Reference**

This document serves as the persistent, long-term roadmap and architectural specification for the Cantor Dashboard UI/UX layer. It defines the interface vision, component relationships, design system, API contracts, state management, and detailed phased deliverables to expose the full backend capabilities of the Ruthenian Typikon logic engine.

---

## 1. Architectural Overview & Data Flow

The Cantor Dashboard is a lightweight, responsive web application structured to run locally on a developer/cantor machine. It features a backend server that queries the liturgical engine and translates complex Python data structures into structured JSON feeds, which are then rendered by a dynamic front-end client.

```mermaid
graph TD
    subgraph Browser (Client-Side HTML5/JS/CSS)
        UI[HTML Viewport] <--> JS[main.js App Controller]
        JS -->|1. AJAX Fetch /api/resolve| Cache[State Cache]
        JS -->|2. AJAX Fetch /api/roadmap| RM[Roadmap Visualizer]
        JS -->|3. SSE Connection| Live[Live-Reload listener]
        UI -->|Print Command| CSS_Print[print.css Media Styles]
    end

    subgraph Server (Python 3 Backend)
        Srv[server.py ThreadingTCPServer]
        Srv -->|API Router| Route[Request Handler]
        Route -->|Resolve Parameters| RE[RuthenianEngine]
        Route -->|Compute Status| RC[Roadmap Collector]
        Route -->|Event Stream| Watch[watch_server.py FS Watcher]
    end

    subgraph Engine & Database
        RE -->|Query| Asset[Stamford Recension JSONs]
        RE -->|Resolve| Computus[Gregorian/Julian Computus]
        RC -->|Read Logs/Specs| Specs[Compliance & Gaps Registries]
    end
```

### High-Level Data Flow
1. **User Action**: The user selects a date, toggles a setting (e.g., switching to Julian Paschalion or enabling Quick-Reference mode), or filters clergy cues.
2. **State Synchronization**: `main.js` captures control state changes and immediately refreshes the active viewport. Liturgical settings trigger a fetch request, appending parameters to the URL query string.
3. **API Dispatch & Resolve**: The backend `server.py` parses parameters, instantiates or updates `RuthenianEngine` with overridden configurations, executes the resolution path, and returns the context, booklet text, and trace logs.
4. **Hot-Reload Pipe**: The file watcher `watch_server.py` monitors all backend and asset modifications, broadcasting reload signals via SSE to ensure immediate frontend updates during development without manual refreshes.

---

## 2. Design System & Visual Philosophy

To provide a premium and state-of-the-art feel, the Cantor Dashboard adheres to strict visual rules that blend traditional ecclesiastical typography with modern, high-contrast, semi-transparent user interfaces (glassmorphism).

### Color Tokens (CSS Variables)
```css
:root {
  /* Core Brand Colors */
  --bg-primary: #0f1015;          /* Deep obsidian canvas */
  --bg-secondary: rgba(22, 24, 33, 0.85); /* Glass pane background */
  --border-color: rgba(255, 255, 255, 0.08); /* Subtle hairline borders */
  
  /* Text Color Hierarchy */
  --text-main: #e2e8f0;           /* Soft white for primary reading */
  --text-muted: #94a3b8;          /* Slate gray for secondary text/labels */
  --text-dark: #000000;           /* Pure black for high-contrast print */

  /* Liturgical Visual Cues */
  --gold-accent: #d4af37;         /* Warm liturgical gold for titles & accents */
  --gold-hover: #f3e5ab;          /* Soft ivory-gold for hover states */
  --rubric-color: #ef4444;        /* Crimson red representing traditional red rubrics */
  --actor-badge-bg: rgba(212, 175, 55, 0.15); /* Translucent gold backdrop */

  /* Status Colors */
  --status-success: #10b981;      /* Emerald for completed/verified logic gates */
  --status-warning: #f59e0b;      /* Amber for stubbed/partially-complete layers */
  --status-error: #ef4444;        /* Red for missing assets or failed tests */
}
```

### Typography System
- **Liturgical Texts (Booklet & Digest)**:
  - Font Family: `Cardo`, `Georgia`, serif;
  - Font Size: Fluid adjustment via CSS variables (`--booklet-font-size`, default: `1.15rem`).
  - Drop Caps: Set on paragraph starts in the booklet (`float: left; font-size: 3rem; color: var(--gold-accent); margin-right: 0.5rem; font-family: Cinzel, serif`).
- **UI & Controls**:
  - Font Family: `Inter`, `system-ui`, sans-serif;
  - Accent Headings: `Cinzel`, serif; (used for tab labels and main dashboard banners).

### UX Layout Schematics
- **Interactive States**: Hovering buttons/cards triggers scale changes (`transform: translateY(-2px)`) and glows (`box-shadow: 0 0 12px rgba(214,175,55,0.2)`).
- **Glassmorphism**: Panels utilize `backdrop-filter: blur(12px)` and thin border overlays to establish visual depth.

---

## 3. UI Component Architecture

The interface is structured as a single-page application (SPA) with a persistent sidebar and tab-panel layout.

```
+-------------------------------------------------------------------------+
| [BANNER]           C A N T O R   D A S H B O A R D          (SSE Status) |
+------------------+------------------------------------------------------+
|                  | [SETTINGS COLLAPSIBLE DRAWER]                        |
|                  | > Paschalion: (Julian | *Gregorian)                  |
|  [TABS]          | > Recension:  (*Stamford | Lviv)                     |
|                  | > Temple Feast: [ MM / DD ]                          |
|  [x] Date        | > Digest Mode:  (*Full     | Quick)                  |
|      Resolver    +------------------------------------------------------+
|                  | [RESOLVER MAIN PANELS]                               |
|  [ ] Book        | +-----------------------------+ +------------------+ |
|      Browser     | | [BOOKLET READ PANE]         | | [CONTEXT WIDGET] | |
|                  | | Toggles: [Clergy Cues] [+/-]| | Tone: 4          | |
|  [ ] Linguistic  | |                             | | Rank: Double     | |
|      Auditor     | | "Blessed is the Kingdom..." | | Season: Pascha   | |
|                  | | [PRIEST]: (Text cue)        | | is_lent: False   | |
|  [ ] Roadmap &   | |                             | +------------------+ |
|      Health      | | [DIGEST MD PANE]            | | [TRACE LOG PAN]  | |
|                  | | * 1. Psalm 103 (read)       | | [Trace filters]  | |
|                  | +-----------------------------+ +------------------+ |
+------------------+------------------------------------------------------+
```

### Core Viewport Sections
1. **Sidebar Navigation**: Triggers tab switching between Date Resolver, Book Browser, Linguistic Auditor, and Roadmap & Health Explorer.
2. **Liturgical Settings Drawer**: Collapsible configuration card with inputs binding directly to client-side session storage.
3. **Double-Pane Output Area**:
   - Left Side: Double tab showing the formatted **Service Booklet** and raw Markdown **Typikon Digest**.
   - Right Side: Context Metadata Summary Widget and full Engine Trace logs.

---

## 4. API Request/Response Contracts

### 4.1 `/api/resolve`
Returns the resolved liturgical parameters, booklet text, digest text, and execution trace for a given date.

- **Method**: `GET`
- **Query Parameters**:
  - `date`: String (`YYYY-MM-DD`, required).
  - `paschalion`: String (`gregorian` | `julian`, default: `gregorian`).
  - `version`: String (`stamford_2014` | `lviv_2018`, default: `stamford_2014`).
  - `temple_feast`: String (`MM-DD`, optional, default: null).
  - `digest_mode`: String (`full` | `quick`, default: `full`).

- **Success Response (JSON)**:
  ```json
  {
    "status": "success",
    "date": "2026-06-09",
    "metadata": {
      "tone": 4,
      "eothinon": 10,
      "season": "Pascha",
      "rank": "Double",
      "title": "Tuesday of the Third Week after Pascha",
      "is_lent": false,
      "weeks_after_pentecost": 0,
      "is_bright_week": false
    },
    "booklet_html": "<div class='liturgical-booklet'>...</div>",
    "digest_markdown": "# Typikon Digest for Tuesday...\n...",
    "trace_logs": [
      { "level": "step", "message": "Resolving date: 2026-06-09" },
      { "level": "warning", "message": "No specific Menaion entry override for this date" }
    ]
  }
  ```

### 4.2 `/api/roadmap`
Returns the overall health, variant compliance, and logic gate statuses.

- **Method**: `GET`
- **Success Response (JSON)**:
  ```json
  {
    "status": "success",
    "wings": {
      "logic": 100,
      "structures": 95,
      "assets": 10,
      "docs": 100,
      "ui": 85
    },
    "matins_gates": [
      { "gate": 1, "name": "Six Psalms (Hexapsalmos)", "status": "completed" },
      { "gate": 2, "name": "Great Litany & God is the Lord", "status": "completed" },
      { "gate": 3, "name": "Kathismata Readings", "status": "completed" },
      { "gate": 13, "name": "Matins Dismissal & Litany", "status": "stubbed" }
    ],
    "variant_matrix": {
      "presanctified_liturgy": "stubbed",
      "vesperal_liturgy": "stubbed",
      "great_compline": "missing",
      "daily_vespers": "completed"
    },
    "unresolved_gaps": [
      "Missing MENAION translation overrides for October feasts",
      "Lviv recension text assets stubbed for Lent"
    ]
  }
  ```

---

## 5. Phased Roadmap Deliverables

The development of the Cantor Dashboard is broken down into structured phases.

### Phase 1: Liturgical Parameter Overrides (Immediate)
*Goal: Expose backend engine configuration variables in the UI settings drawer.*
- Allows the user to dynamically adjust:
  - **Paschalion computation** (Gregorian vs. Julian calendar rules, passing `paschalion` to the resolver).
  - **Recension version** (Standard Stamford vs. Lviv text files, passing `version` to the resolver).
  - **Temple Patronal Feast** (defining the local parish saint override, passing `temple_feast` as `(month, day)` to trigger special vigil and rank promotions).
  - **Digest Mode** (Full complete instructions vs. Quick-Reference daily outlines, passing `digest_mode` to toggle Compline/Midnight Office inclusion).
- Frontend UI elements send selected inputs to the backend in real-time, instantly resolving the day's texts according to custom liturgical settings.

### Phase 2: Project Health, Coverage Maps & Feast Cycle Explorer (Immediate)
*Goal: Expose logic gates, stubs, and variant completion lists while introducing the Feast Cycle visualizer.*
- **Encyclopedic Visualizers**:
  - **5 Wings Progress Card**: Completion levels for Logic (100%), Structures (95%), Assets (10%), Docs (100%), and UI (85%).
  - **Variant Coverage Matrix**: A grid representing the resolution status of all major service schemas (e.g., Daily Vespers, Presanctified Liturgy, Vesperal Liturgy, Great Compline).
  - **13 Matins Logic Gates**: A checklist detailing the execution path coverage for Byzantine Matins.
  - **Trace Log Filters**: Tab controls to group console traces by level (All, Steps, warnings/errors).
- **Feast Cycle Visualizer**:
  - **Unified Timeline Row**: A horizontal grid displaying an entire Great Feast span (Forefeast preparation days, the double-bordered Feast day, Afterfeast extension days, and the final Apodosis/Leave-taking day).
  - **Fixed vs. Relative Guides**: Interactive split-pane showing which parts of the service remain fixed (e.g., festal troparia) and how relative parts (e.g., weekday tones, Sunday intersections) are determined.
  - **Wave-Grouped Catalog**: An encyclopedic listing of services and booklets grouped under active liturgical waves (e.g., "Exaltation of the Cross Cycle") rather than simple calendar dates, matching the card-catalog structure of liturgical booklets.

### Phase 3: Advanced Liturgical Chant Renderers (Future)
*Goal: Enrich booklet with parallel language options and chanting helpers.*
- Supports bilingual side-by-side print columns (English/Slavonic/Ukrainian).
- Renders melody incipits or Kyivan/Neumatic musical notations.
- Integrates regional chant variants selector.

### Phase 4: Booklet Customization & Print Enhancements (Long-Term/End of List)
*Goal: Provide formatting options so cantors can use the output at the music stand or print it.*
- Adds a **Clergy Cues Toggle** (Priest/Deacon line filter) to hide instruction cues.
- Adds **Text Size Scalers** targeting font-size CSS variables.
- Optimizes print CSS stylesheet in `style.css` (hiding UI buttons, formatting pages for print).
- Renders structural engine variables (`is_lent`, `is_bright_week`, `weeks_after_pentecost`) in the Context Panel.

---

## 6. Client State Lifecycle & Validation

### Client State Model
The frontend client maintains UI state in local memory, synchronized with `localStorage` to preserve settings between browser loads.
```js
const ClientState = {
  // Liturgical parameters (passed to API)
  paschalion: localStorage.getItem('paschalion') || 'gregorian',
  version: localStorage.getItem('version') || 'stamford_2014',
  templeFeast: localStorage.getItem('templeFeast') || '',
  digestMode: localStorage.getItem('digestMode') || 'full',
  
  // UX controls (client-side only)
  hideClergy: localStorage.getItem('hideClergy') === 'true',
  textSize: parseInt(localStorage.getItem('textSize')) || 100,
  activeTab: localStorage.getItem('activeTab') || 'tab-resolver'
};
```

### Automated UI Validation Strategy
To guarantee UI stability across modifications:
1. **Unit Verification**: Validate `/api/resolve` parameter parsing using backend unit tests.
2. **DOM Validation**: Frontend event handlers are bound using explicit, descriptive element IDs (e.g. `opt-paschalion`, `btn-text-increase`, `chk-hide-clergy`) to enable reliable automated testing.
3. **CSS Regressions**: Ensure standard CSS custom properties are manipulated directly rather than overriding styling inline to prevent component misalignment.
