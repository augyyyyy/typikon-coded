class ComplineFormatterMixin:
    def _format_resolve_compline_troparia(self, res, context):
        if not res: return ""
        if isinstance(res, dict) and res.get("type") == "troparia_stack":
            comps = self._format_troparia_stack_components(res.get("components", []), context)
            if "Glory..." in comps:
                # Replace comma before Glory... with semicolon
                comps = comps.replace(", Glory...", "; Glory...")
            label = "Troparia"
            if "kontakion" in comps.lower():
                label = "Kontakion" if "Glory..." not in comps else "Kontakia"
            return f"{label}: {comps}."
        return f"Troparia: {self.humanize_key(res)}."


    def _format_resolve_compline_lord_of_hosts(self, res, context):
        if not res: return ""
        ref = res.get("ref_key", "")
        if ref == "lord_of_hosts_tone_6":
            return "Lord of Hosts: We sing 'Lord of hosts, be with us...' in Tone 6."
        return f"Lord of Hosts: We read the Kontakion of the Feast."

