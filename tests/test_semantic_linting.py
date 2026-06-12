import pytest
from datetime import date
from ruthenian_engine import RuthenianEngine

class TestSemanticLinting:
    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = RuthenianEngine(base_dir=".")

    def test_june_12_2026_co_suffering_theotokos(self):
        """
        Friday of the Co-suffering of the Most Holy Theotokos (June 12, 2026):
        - Dolnytsky Rubric: Saint of the day (Venerables Onuphrius & Peter of Athos) is suppressed.
        - Liturgy template must be 'festal_only' (bypassing Wednesday/Friday Cross precedence).
        - Matins canon total count must be 12 (Feast canon only).
        - Saints list in context must be cleared to prevent leakage.
        """
        target_date = date(2026, 6, 12)
        context = self.engine.get_liturgical_context(target_date)
        rubrics = self.engine.resolve_rubrics(context)

        # 1. Assert Saint Suppression
        assert rubrics["variables"].get("suppress_menaion_saint") is True
        assert len(context.get("saints", [])) == 0

        # 2. Verify Matins Canon Count (Feast only on 12)
        canon_stack = self.engine.resolve_canon_stack(context)
        assert canon_stack is not None
        assert canon_stack.get("total_count") == 12
        dist = canon_stack.get("distribution", [])
        assert sum(d.get("qty", 0) for d in dist) == 12

        # 3. Verify Liturgy Propers select 'festal_only' template (bypasses Wed/Fri Cross)
        liturgy_hymns = self.engine.resolve_liturgy_hymns(context, rubrics)
        assert len(liturgy_hymns["components"]) == 2
        assert liturgy_hymns["components"][0]["type"] == "troparion"
        assert liturgy_hymns["components"][0]["source"] == "feast"
        assert liturgy_hymns["components"][1]["type"] == "kontakion"
        assert liturgy_hymns["components"][1]["source"] == "feast"

        # 4. Verify Hours Troparia resolves to Feast Troparion and Kontakion (no Saint)
        hours_troparia = self.engine.resolve_hours_troparia(context, rubrics)
        assert len(hours_troparia["components"]) == 1
        assert hours_troparia["components"][0] == "trop_feast"

        hours_kontakion = self.engine.resolve_hours_kontakion(context, rubrics)
        assert hours_kontakion["type"] == "kontakion"
        assert hours_kontakion["source"] == "feast"

    def test_june_11_2026_apodosis_eucharist_polyeleos_saint(self):
        """
        Apodosis of the Eucharist + Apostles Bartholomew & Barnabas (June 11, 2026):
        - Vespers stichera total count must be 10 (6 Feast + 4 Saint).
        - Matins canon total count must be 14 (10 Feast + 4 Saint).
        - Compline canon should return the Theotokos canon (Feast canon suppressed).
        """
        target_date = date(2026, 6, 11)
        context = self.engine.get_liturgical_context(target_date)
        rubrics = self.engine.resolve_rubrics(context)

        # 1. Vespers Stichera Distribution (10 total: 6 Feast, 4 Saint)
        vespers_res = self.engine.resolve_vespers_stichera(context)
        assert vespers_res.get("total_count") == 10
        dist = vespers_res.get("distribution", [])
        assert sum(d.get("qty", 0) for d in dist) == 10
        assert any(d.get("type") == "feast" and d.get("qty") == 6 for d in dist)
        assert any(d.get("type") == "saint" and d.get("qty") == 4 for d in dist)

        # 2. Matins Canon (14 total: 10 Feast, 4 Saint)
        canon_stack = self.engine.resolve_canon_stack(context)
        c_dist = canon_stack.get("distribution", [])
        assert sum(c.get("qty", 0) for c in c_dist) == 14
        assert any(c.get("type") == "feast" and c.get("qty") == 10 for c in c_dist)
        assert any(c.get("type") == "saint" and c.get("qty") == 4 for c in c_dist)

        # 3. Compline Canon (Feast canon suppressed, returns theotokos from Octoechos)
        compline_canon = self.engine.resolve_compline_canon(context)
        assert compline_canon is not None
        assert compline_canon.get("subject") == "theotokos"
        assert compline_canon.get("book") == "octoechos"

    def test_january_6_2026_theophany(self):
        """
        Great Feast of Theophany (January 6, 2026):
        - Vespers stichera total count must be 8 (all Feast).
        - Matins praises stichera count must be 4 (all Feast).
        - Matins canon total count must be 12 (all Feast).
        - Liturgy template must be 'festal_only'.
        """
        target_date = date(2026, 1, 6)
        context = self.engine.get_liturgical_context(target_date)
        rubrics = self.engine.resolve_rubrics(context)

        # 1. Vespers Stichera (8 total, all Feast)
        vespers_res = self.engine.resolve_vespers_stichera(context)
        assert vespers_res.get("total_count") == 8
        dist = vespers_res.get("distribution", [])
        assert any(d.get("source") == "menaion" and d.get("type") == "feast" and d.get("qty") == 8 for d in dist)

        # 2. Matins Praises (4 total, all Feast)
        praises_res = self.engine.resolve_praises_stack(context)
        assert praises_res.get("total_count") == 4
        p_dist = praises_res.get("distribution", [])
        assert any(p.get("source") == "menaion" and p.get("type") == "feast" and p.get("qty") == 4 for p in p_dist)

        # 3. Matins Canon (12 total, all Feast)
        canon_stack = self.engine.resolve_canon_stack(context)
        assert canon_stack.get("total_count") == 12
        c_dist = canon_stack.get("distribution", [])
        assert any(c.get("source") == "feast" and c.get("type") == "feast" and c.get("qty") == 12 for c in c_dist)

        # 4. Liturgy Hymns (festal_only: 2 components - feast troparion, feast kontakion)
        liturgy_hymns = self.engine.resolve_liturgy_hymns(context, rubrics)
        assert len(liturgy_hymns["components"]) == 2
        assert liturgy_hymns["components"][0]["type"] == "troparion"
        assert liturgy_hymns["components"][0]["source"] == "feast"
        assert liturgy_hymns["components"][1]["type"] == "kontakion"
        assert liturgy_hymns["components"][1]["source"] == "feast"
