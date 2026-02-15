import json
import logging
import os
from typing import List, Dict, Any
from .config import DATA_DIR, OUTPUT_DIR, INPUT_CHUNKS_PATH, LLMConfig
from .extraction import BaseExtractor, get_extractor
from .graph_builder import GraphBuilder
from .mermaid_renderer import MermaidRenderer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.extractor = get_extractor(config)
        self.graph_builder = GraphBuilder()

    def load_chunks(self) -> List[Dict[str, Any]]:
        try:
            with open(INPUT_CHUNKS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load input chunks from {INPUT_CHUNKS_PATH}: {e}")
            return []

    def run(self):
        logger.info("Starting GraphRAG Pipeline...")
        
        # 1. Load Data
        chunks = self.load_chunks()
        logger.info(f"Loaded {len(chunks)} chunks.")

        # 1.5 Load Existing Graph (if persistence is enabled/file exists)
        json_output_path = OUTPUT_DIR / "graph.json"
        if os.path.exists(json_output_path):
            logger.info(f"Found existing graph at {json_output_path}. Loading...")
            self.graph_builder.load_from_json(json_output_path)
            
        # 2. Process each chunk
        for chunk in chunks:
            chunk_id = chunk.get("id")
            chunk_text = chunk.get("text")
            
            logger.info(f"Processing Chunk {chunk_id}...")
            
            # Extract
            extraction_result = self.extractor.extract(chunk_text, chunk_id)
            
            # Build Graph
            self.graph_builder.add_chunk_data(extraction_result, chunk_id)

        # 3. Export JSON
        graph_json = self.graph_builder.export_json()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        json_output_path = OUTPUT_DIR / "graph.json"
        
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_json, f, indent=2)
        logger.info(f"Graph JSON saved to {json_output_path}")

        # 4. Render Mermaid
        renderer = MermaidRenderer(graph_json)
        mermaid_text = renderer.render()
        
        mermaid_output_path = OUTPUT_DIR / "graph.mmd"
        with open(mermaid_output_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_text)
        logger.info(f"Mermaid Graph saved to {mermaid_output_path}")

        return graph_json, mermaid_text
