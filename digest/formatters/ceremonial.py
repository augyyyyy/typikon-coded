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
            return f"The holy doors are opened{note_str}."
        elif state == "closed":
            return f"The holy doors are closed{note_str}."
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

