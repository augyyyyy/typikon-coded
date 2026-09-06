from typing import List, Dict, Any, Optional

class FootnoteFormatterMixin:
    """Mixin providing formatting methods for Dolnytsky Synodal Footnotes in Typikon digests."""

    def _format_inline_synodal_callout(self, footnote: Dict[str, Any]) -> str:
        """Format a single inline synodal callout block for the Right Panel digest."""
        if not footnote:
            return ""
        fn_num = footnote.get("number", "")
        category = footnote.get("category", "rubric_alternative")
        text = footnote.get("text", "").strip()
        
        cat_badge = "Parish Custom" if category == "parish_custom" else "Synodal Rubric Alternative"
        return f"> 💡 **Dolnytsky Note [^{fn_num}] ({cat_badge}):** {text}"

    def _format_service_synodal_callouts(self, footnotes: List[Dict[str, Any]], max_inline: int = 3) -> str:
        """Format top actionable synodal callouts for a specific service card."""
        if not footnotes:
            return ""
        
        actionable = [f for f in footnotes if f.get("category") in ("rubric_alternative", "parish_custom")]
        if not actionable:
            return ""
            
        lines = []
        for fn in actionable[:max_inline]:
            callout = self._format_inline_synodal_callout(fn)
            if callout:
                lines.append(callout)
                
        return "\n\n".join(lines)

    def _format_synodal_footnotes_section(self, footnotes: List[Dict[str, Any]]) -> str:
        """Format the complete Synodal Footnotes and Alternatives appendix for the day digest."""
        if not footnotes:
            return ""
            
        lines = ["## SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES (DOLNYTSKY TYPIKON)", ""]
        for fn in footnotes:
            fn_num = fn.get("number", "")
            text = fn.get("text", "").strip()
            cat = fn.get("category", "rubric_alternative").replace("_", " ").title()
            part = fn.get("typikon_part", "").replace("_", " ").title()
            lines.append(f"**[^{fn_num}] ({cat} - {part}):** {text}  \n")
            
        return "\n".join(lines)
