class LentenFormatterMixin:
    def _format_resolve_lenten_prokeimenon(self, res, context):
        if not res:
            return ""
        if res.get("type") == "prokeimenon":
            return f"Prokeimenon: {self.humanize_key(res.get('ref_key'))}"
        parts = []
        for comp in res.get("components", []):
            if comp.get("type") == "prokeimenon":
                parts.append(f"Prokeimenon: {self.humanize_key(comp.get('ref_key'))}")
            elif comp.get("type") == "reading":
                parts.append(f"Reading from {comp.get('source', '').capitalize()}")
        return "\n".join(parts)


    def _format_resolve_lenten_ending(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            if c_type == "lenten_troparia_block":
                troparia = []
                for t in comp.get("components", []):
                    name = self.humanize_key(t.get("ref_key"))
                    if t.get("prostration"):
                        troparia.append(f"{name} (with prostration)")
                    else:
                        troparia.append(name)
                parts.append(f"Lenten Troparia: {'; '.join(troparia)}")
            elif c_type == "fixed_ref":
                parts.append(self.humanize_key(comp.get("ref_key")))
            elif c_type == "prayer_ephrem":
                count = comp.get("prostration_count", 0)
                parts.append(f"Prayer of St. Ephrem ({count} prostrations)")
            elif c_type == "come_let_us_worship":
                parts.append("Come, let us worship (with final prostrations)")
        return "\n".join(parts)


    def _format_resolve_lenten_sessional(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_lenten_aposticha(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_bridegroom_aposticha(self, res, context):
        if not res:
            return ""
        return f"Bridegroom Aposticha: {res.get('rubric_note')}"


    def _format_resolve_encomia_station(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_presanctified_transfer(self, res, context):
        if not res:
            return ""
        action = res.get("transfer_action", {})
        priest = action.get("priest_action", "")
        deacon = action.get("deacon_action", "")
        covering = action.get("covering", "")
        
        parts = [
            f"At the Kathisma: {res.get('rubric', {}).get('note', '')}",
            f"During the Kathisma: {priest}",
            f"The deacon: {deacon}",
            f"After placement: {covering}"
        ]
        if "special_note" in action:
            parts.append(action["special_note"])
        return "; ".join(parts) + "."


    def _format_resolve_presanctified_entrance(self, res, context):
        if not res:
            return ""
        ent_type = res.get("entrance_type", "censer")
        rub = res.get("rubric", {})
        title = rub.get("title", "Entrance")
        
        if ent_type == "gospel":
            gospel_ref = self.humanize_key(res.get("gospel_ref", ""))
            return f"Entrance: {title} with the Gospel book (Gospel: {gospel_ref})."
        
        roles = rub.get("roles", {})
        deacon_role = roles.get("deacon", "")
        priest_role = roles.get("priest", "")
        
        parts = [f"Entrance: {title} with the censer"]
        if deacon_role:
            parts.append(f"Deacon: {deacon_role}")
        if priest_role:
            parts.append(f"Priest: {priest_role}")
        return "; ".join(parts) + "."


    def _format_resolve_lenten_prokeimenon(self, res, context):
        if not res:
            return ""
        if res.get("type") == "sequence":
            parts = []
            for comp in res.get("components", []):
                c_type = comp.get("type")
                if c_type == "prokeimenon":
                    parts.append(f"Prokeimenon ({self.humanize_key(comp.get('ref_key', ''))})")
                elif c_type == "reading":
                    parts.append(f"Reading from {comp.get('source', '').capitalize()}")
            return "At the readings: " + " then ".join(parts) + "."
        else:
            ref = res.get("ref_key", "")
            return f"Prokeimenon: {self.humanize_key(ref)}."


    def _format_resolve_lenten_ending(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            if c_type == "lenten_troparia_block":
                block_parts = []
                for sub in comp.get("components", []):
                    ref = sub.get("ref_key", "")
                    prost = " with a great prostration" if sub.get("prostration") else ""
                    block_parts.append(f"{self.humanize_key(ref)}{prost}")
                parts.append("Lenten Troparia: " + "; ".join(block_parts))
            elif c_type == "fixed_ref":
                parts.append(self.humanize_key(comp.get("ref_key", "")))
            elif c_type == "prayer_ephrem":
                ref = comp.get("ref_key", "")
                cnt = comp.get("prostration_count", 0)
                parts.append(f"Prayer of St. Ephrem ({self.humanize_key(ref)}) with {cnt} prostrations")
            elif c_type == "come_let_us_worship":
                parts.append("Come let us worship (3x) with prostrations")
            else:
                parts.append(self.humanize_key(str(comp)))
        return "At the Lenten Ending:\n" + "\n".join(f"  - {p}" for p in parts)


    def _format_resolve_lenten_sessional(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        rubric = res.get("rubric_note", "")
        return f"Lenten Sessional: {self.humanize_key(ref)} ({rubric})"


    def _format_resolve_lenten_aposticha(self, res, context):
        if not res:
            return ""
        stichera = [self.humanize_key(s.get("ref", "")) for s in res.get("stichera", [])]
        glory = self.humanize_key(res.get("glory", {}).get("ref", ""))
        now = self.humanize_key(res.get("now", {}).get("ref", ""))
        rubric = res.get("rubric_note", "")
        return f"Lenten Aposticha: {'; '.join(stichera)}. Glory: {glory}. Both now: {now}. ({rubric})"


    def _format_resolve_bridegroom_aposticha(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Bridegroom Aposticha: {note}."


    def _format_resolve_encomia_station(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Lamentations at the Tomb: {note}."

