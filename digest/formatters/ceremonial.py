class CeremonialFormatterMixin:




    def _format_resolve_vestment_color(self, res, context):
        if not res:
            return ""
        color = res.get("color", "")
        alt = res.get("alt", "")
        alt_str = f" or {alt}" if alt else ""
        return f"Vestment colour: {color.capitalize()}{alt_str}."


    def _format_resolve_censing_annotation(self, res, context):
        if not res or not res.get("has_censing"):
            return ""
        prot = res.get("protocol", {})
        desc = prot.get("description", "")
        return f"Censing: {desc}."


    def _format_resolve_door_state(self, res, context):
        if not res:
            return ""
        state = res.get("state", "").lower()
        note = res.get("note", "")
        note_str = f" ({note})" if note else ""
        if state == "open":
            return f"The royal doors are opened{note_str}."
        elif state == "closed":
            return f"The royal doors are closed{note_str}."
        return f"Royal Doors: {state.upper()}{note_str}."


    def _format_resolve_curtain_state(self, res, context):
        if not res:
            return ""
        state = res.get("state", "")
        note = res.get("note", "")
        note_str = f" - {note}" if note else ""
        return f"Curtain: {state.upper()}{note_str}."


    def _format_resolve_vestment_set(self, res, context):
        if not res:
            return ""
        vest = ", ".join(res.get("vestments", []))
        note = res.get("note", "").strip()
        if note.startswith("-"):
            note = note.lstrip("-").strip()
        if "phelonion blessed and kissed" in note.lower():
            note = "The phelonion is blessed and kissed before the Entrance."
            note_str = f" {note}"
        else:
            note_str = f" — {note}" if note else ""
        return f"Vestments ({res.get('clergy_type', '')}): {vest}.{note_str}"


    def _format_resolve_bow_type(self, res, context):
        if not res:
            return ""
        if res.get("forbidden"):
            return f"Bows/Prostrations: Forbidden ({res.get('reason', '')})."
        bt = res.get("bow_type", "")
        cnt = res.get("count", 1)
        note = res.get("note", "")
        note_str = f" - {note}" if note else ""
        return f"Bow: {bt} x{cnt}{note_str}."


    def _format_resolve_hand_position(self, res, context):
        if not res:
            return ""
        desc = res.get("description", "")
        return f"Hand Position: {desc}."


    def _format_resolve_role_view(self, res, context):
        return str(res)


    def _format_resolve_cantor_signal(self, res, context):
        return str(res)


    def _format_resolve_deacon_role(self, res, context):
        if not res:
            return ""
        ref = res.get("ordo_ref", "")
        inst = res.get("instruction", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"Deacon Role{ref_str}: {inst}"


    def _format_resolve_concelebration_roles(self, res, context):
        if not res:
            return ""
        if not res.get("concelebrating"):
            return res.get("roles", {}).get("principal", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        roles = res.get("roles", {})
        principal = roles.get("principal", "")
        concelebrants = "; ".join(roles.get("concelebrants", []))
        return f"Concelebration{ref_str}: (Principal) {principal} (Concelebrants) {concelebrants}"


    def _format_resolve_vespers_censing_sequence(self, res, context):
        if not res:
            return ""
        who = res.get("who", "clergy")
        desc = res.get("description", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        seq = res.get("sequence", [])
        seq_steps = []
        for step in seq:
            target = step.get("target", "").replace("_", " ").title()
            note = step.get("note", "")
            note_str = f" ({note})" if note else ""
            seq_steps.append(f"{target}{note_str}")
        seq_str = " -> ".join(seq_steps)
        seq_block = f" Path: {seq_str}" if seq_steps else ""
        return f"Censing by {who}{ref_str}: {desc}{seq_block}"


    def _format_resolve_litya_procession(self, res, context):
        if not res:
            return ""
        parts = []
        if "procession" in res:
            parts.append(f"Procession: {res['procession']}")
        if "petitions" in res:
            parts.append(f"Petitions: {res['petitions']}")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        content = " ".join(parts)
        return f"Litya{ref_str}: {content}"




    def _format_resolve_polyeleos_movement(self, res, context):
        if not res:
            return ""
        mov = res.get("clergy_movement", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"Polyeleos Movement{ref_str}: {mov}"


    def _format_resolve_matins_gospel_censing(self, res, context):
        if not res:
            return ""
        who = res.get("who", "")
        censing = res.get("censing", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"Matins Gospel Censing by {who.capitalize()}{ref_str}: {censing}"


    def _format_resolve_proskomedia_vessels(self, res, context):
        if not res:
            return ""
        prep = res.get("vessel_preparation", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"Proskomedia Vessels Preparation{ref_str}: {prep}"


    def _format_resolve_liturgy_entrances(self, res, context):
        if not res:
            return ""
        ent_type = res.get("entrance_type", "").capitalize()
        proc = res.get("procession", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"{ent_type} Entrance{ref_str}: {proc}"




    def _format_resolve_presanctified_censing(self, res, context):
        if not res:
            return ""
        censing = res.get("censing", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" [{ref}]" if ref else ""
        return f"Presanctified Censing{ref_str}: {censing}"



