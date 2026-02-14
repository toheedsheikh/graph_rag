from typing import Dict, Any

class MermaidRenderer:
    def __init__(self, graph_json: Dict[str, Any]):
        self.data = graph_json

    def render(self) -> str:
        """
        Generates Mermaid TD graph string from the graph JSON.
        """
        lines = ["graph TD"]
        
        # Add styles/comments
        lines.append(" %% =========================")
        lines.append(" %% Generated Graph")
        lines.append(" %% =========================")

        # Render Nodes
        # Format: ID["Label<br/><b>Tags/Attributes</b>: key=value; key=value"]
        
        for node in self.data.get("nodes", []):
            node_id = node.get("id")
            # Sanitize ID for Mermaid (remove spaces or special chars if used as ID, strict alphanumeric preferred)
            safe_id = self._sanitize_id(node_id)
            
            entity_type = node.get("type", "Entity")
            attributes = node.get("attributes", {})
            
            # Construct label
            # We want: "type: name<br/><b>Attributes</b>: ..."
            # Check for "description" in attributes to use as main label part if available, else just type
            
            # The assignment example: Swiggy["Company: Swiggy Limited<br/>..."]
            # My gold standard has: Swiggy (Company), attribs: Strategy...
            
            primary_label = f"{entity_type}: {node_id}"
            
            # Format attributes string
            attr_parts = []
            for k, v in attributes.items():
                if k.lower() == "description":
                    # If description exists, maybe prepend it? 
                    # Actually, the example shows "Company: Swiggy Limited" where "Swiggy Limited" might be from desc or name?
                    # Let's stick to the example pattern.
                    pass
                else:
                    attr_parts.append(f"{k}={v}")
            
            attr_str = "; ".join(attr_parts)
            
            if attr_str:
                label = f"{primary_label}<br/><b>Tags/Attributes</b>: {attr_str}"
            else:
                label = primary_label
            
            lines.append(f' {safe_id}["{label}"]')

        lines.append("")
        
        # Render Edges
        # Format: A -->|relation| B
        for edge in self.data.get("edges", []):
            source = self._sanitize_id(edge.get("source"))
            target = self._sanitize_id(edge.get("target"))
            relation = edge.get("relation", "related_to")
            
            lines.append(f' {source} -->|{relation}| {target}')

        return "\n".join(lines)

    def _sanitize_id(self, text: str) -> str:
        """
        Simple sanitizer for Mermaid node IDs.
        Mermaid IDs cannot have spaces or special characters generally without quotes, 
        but we are using the ID in the bracket `ID["Label"]`. 
        The *ID* part must be clean. 
        """
        return text.replace(" ", "").replace("-", "").replace("&", "")
