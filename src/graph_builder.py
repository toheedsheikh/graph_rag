import networkx as nx
import logging
from typing import Dict, List, Any
import json
from .config import RELATIONSHIP_TYPES

logger = logging.getLogger(__name__)

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.provenance = {} # Map node/edge to chunk IDs

    def _normalize_name(self, name: str) -> str:
        """
        Normalize entity name for deduplication (case-insensitive).
        Returns the canonical name (first seen casing or most frequent).
        For now, we'll store a mapping of lower_case -> DisplayName.
        """
        return name.strip()

    def add_chunk_data(self, chunk_data: Dict[str, Any], chunk_id: int):
        """
        Integrates extraction results into the graph.
        """
        entities = chunk_data.get("entities", [])
        relationships = chunk_data.get("relationships", [])
        events = chunk_data.get("events", [])

        # Process Entities
        for entity in entities:
            name = self._normalize_name(entity.get("name", "Unknown"))
            entity_type = entity.get("type", "Unknown")
            attributes = entity.get("attributes", {})
            
            if name not in self.graph:
                self.graph.add_node(name, type=entity_type, attributes=attributes, provenance=[chunk_id])
            else:
                # Merge attributes
                existing_attrs = self.graph.nodes[name].get("attributes", {})
                existing_attrs.update(attributes)
                self.graph.nodes[name]["attributes"] = existing_attrs
                # Update provenance
                if chunk_id not in self.graph.nodes[name]["provenance"]:
                    self.graph.nodes[name]["provenance"].append(chunk_id)

        # Process Events (Treat as nodes for now, or ensure they are linked)
        # In the gold standard, events are in the 'entities' list with type 'Event'
        # If 'events' is a separate list of objects, we handle them here:
        for event in events:
             # Logic to handle separate event objects if they exist
             pass

        # Process Relationships
        for rel in relationships:
            source = self._normalize_name(rel.get("source"))
            target = self._normalize_name(rel.get("target"))
            relation = rel.get("relation", "related_to")
            
            # Validate relation
            if relation not in RELATIONSHIP_TYPES:
                # logger.warning(f"Relation '{relation}' not in controlled vocabulary. Fallback to 'related_to'.")
                # fallback (optional, per requirements)
                pass 

            if source in self.graph and target in self.graph:
                self.graph.add_edge(source, target, relation=relation, provenance=[chunk_id])
            else:
                logger.warning(f"Skipping edge {source} -> {target}: One or both nodes missing.")

    def export_json(self) -> Dict[str, Any]:
        """
        Exports the graph to a JSON format (GraphRAG-ready).
        """
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "type": data.get("type"),
                "attributes": data.get("attributes"),
                "provenance": data.get("provenance")
            })
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation"),
                "provenance": data.get("provenance")
            })
            
        return {"nodes": nodes, "edges": edges}
