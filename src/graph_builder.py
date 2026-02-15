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
        self.name_map = {} # Lowercase -> Canonical Name (e.g., "tesla" -> "Tesla")

    def _normalize_name(self, name: str) -> str:
        """
        Normalize entity name for deduplication (case-insensitive).
        Returns the canonical name (first seen casing or most frequent).
        """
        name_clean = name.strip()
        name_lower = name_clean.lower()
        
        if name_lower in self.name_map:
            return self.name_map[name_lower]
        
        # New entity, store mapping
        self.name_map[name_lower] = name_clean
        return name_clean

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

    def load_from_json(self, json_path: str):
        """
        Loads an existing graph from a JSON file (GraphRAG format) to enable incremental updates.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore Nodes
            for node_data in data.get("nodes", []):
                node_id = node_data.get("id")
                if node_id:
                    self.graph.add_node(
                        node_id, 
                        type=node_data.get("type"), 
                        attributes=node_data.get("attributes", {}),
                        provenance=node_data.get("provenance", [])
                    )
                    # Rebuild name map
                    self.name_map[node_id.lower()] = node_id

            # Restore Edges
            for edge_data in data.get("edges", []):
                source = edge_data.get("source")
                target = edge_data.get("target")
                if source and target:
                    self.graph.add_edge(
                        source, 
                        target, 
                        relation=edge_data.get("relation"),
                        provenance=edge_data.get("provenance", [])
                    )
            
            logger.info(f"Loaded existing graph from {json_path} with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

        except FileNotFoundError:
            logger.warning(f"Graph file {json_path} not found. Starting with empty graph.")
        except json.JSONDecodeError:
             logger.error(f"Error decoding JSON from {json_path}. Starting with empty graph.")
        except Exception as e:
            logger.error(f"Failed to load graph from {json_path}: {e}")

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
