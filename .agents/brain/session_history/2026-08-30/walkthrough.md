# Walkthrough: Parish Customizer (Temple Patron & Hierarch Commemorations)

## Overview & Accomplishments
Implemented dynamic parish-level customization across the **Ruthenian Typikon Engine**, **Service Rubrics Digest Generator**, and **Cantor Dashboard Frontend**, enabling the dashboard and generated digests to automatically adapt to any specific church dedication (Lord, Theotokos, Saint) and local hierarchy jurisdiction (Eparchy presets, custom hierarchs, and Sede Vacante modes).

---

## 1. Canonical Logic & Engine Resolvers

### A. Little Entrance 4-Case Matrix (*Ordo Celebrationis §§62–67, Dolnytsky Part V §1*)
* **Case 1 (Temple of the Lord on Sunday)**: Sunday Resurrection Troparion -> Saint Troparion -> Sunday Resurrection Kontakion -> Glory: Saint Kontakion -> Both now: Steadfast Protectress (Temple troparion is omitted).
* **Case 2 (Temple of the Theotokos on Sunday)**: Sunday Resurrection Troparion -> Temple Troparion of the Theotokos -> Saint Troparion -> Sunday Resurrection Kontakion -> Glory: Saint Kontakion -> Both now: Steadfast Protectress / Temple Theotokion.
* **Case 3 (Temple of a Saint on Sunday)**: Sunday Resurrection Troparion -> Temple Patron Troparion -> Saint of the Day Troparion -> Sunday Resurrection Kontakion -> Temple Patron Kontakion -> Glory: Saint of the Day Kontakion -> Both now: Steadfast Protectress.
* **Case 4 (Great Feast of the Lord)**: Festal Troparion (1x) -> Glory, Both now: Festal Kontakion (1x). Total suppression of all lesser commemorations.
* **Weekday Matrix**: Day theme proper -> Temple troparion -> Saint of the day proper -> Day kontakion -> Glory: Saint kontakion -> Both now: Temple kontakion / Steadfast Protectress.

### B. Hierarchical Litanies & Sede Vacante (*Ordo §§2251, 2334*)
* Universal Litany Resolver (`resolve_litany_universal` and `resolve_litany_hierarchy` in `engine/resolvers/common.py`) conjoins names for:
  * Universal Pontiff (Pope)
  * Major Archbishop / Patriarch
  * Metropolitan
  * Local Eparchial Bishop
* **Sede Vacante Substitutions**: Automatic replacement with canonical formulae (*"the vacant Apostolic See of Rome"*, *"the diocesan administrator"*, *"the metropolitan administrator"*).

### C. Dismissal Patron Invocations
* Local Patron Saint Title (e.g. *"our holy father Nicholas, Archbishop of Myra in Lycia, wonderworker"*) is dynamically injected into daily and Sunday dismissals (*"and of holy [Patron], the patron of this holy temple..."*), and suppressed on Great Feasts of the Lord.

---

## 2. Cantor Dashboard Frontend & Server Integration

### A. Parish & Temple Customizer Drawer (`cantor_dashboard/index.html` & `style.css`)
* **Eparchy Presets**: Quick select for major UGCC jurisdictions:
  * *Eparchy of Stamford* (Bishop Paul)
  * *Archeparchy of Philadelphia* (Metropolitan Borys)
  * *Eparchy of St. Nicholas in Chicago* (Bishop Benedict)
  * *Eparchy of St. Josaphat in Parma* (Bishop Bohdan)
  * *Eparchy of Toronto & Eastern Canada* (Bishop Bryan)
  * *Eparchy of Edmonton* (Bishop David)
  * *Custom Hierarchy*
* **Temple Dedication Categories**: Dropdowns for Lord, Theotokos, Saint, and custom feast date `MM-DD`.
* **Hierarch Commemorations Sub-Drawer**: Editable inputs and Sede Vacante toggles for Pope, Patriarch, Metropolitan, and Bishop.
* **Profile Persistence**: Full save, load, and delete support with LocalStorage.

### B. Service Rubrics Digest Dynamic Adaptation (`digest/base.py` & `digest/formatters/liturgy.py`)
* General Info Card renders active parish metadata: `Parish Temple: [Name] ([Type])`.
* Little Entrance table displays the exact Troparia/Kontakia sequence tailored to the active temple.

---

## 3. Verification & Test Evidence

```text
tests/test_session_compliance.py::test_session_compliance PASSED         [100%]
tests/test_temple_little_entrance.py . . . . . .                          [100%]
tests/test_dismissal_resolution.py . . . . . .                            [100%]
tests/test_server_endpoints.py . . . . . .                                [100%]
============================== 406 passed in 104.05s ==============================
```

406 tests pass, 0 tests fail, 40 files changed.
