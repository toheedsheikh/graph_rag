# GraphRAG Assignment - Company Graph Architecture

This repository contains a general-purpose graph construction pipeline designed to translate text chunks into a GraphRAG-ready knowledge graph and Mermaid visualization.

## Features

- **Chunk Extraction**: Extracts Entities, Relationships, and Events from text chunks using LLMs (Gemini via `google-genai`) or Mock Data.
- **Graph Construction**: Builds a networkx graph with deduplication and attribute merging.
- **Export**: Generates both a structured JSON (GraphRAG-ready) and a Mermaid flowchart (visualization-ready).
- **Expandable**: Designed to handle new chunks and extend the graph dynamically.

## Setup

1. **Clone/Download the repository**.
2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configuration**:
   - Create a `.env` file in the root directory.
   - Add your Gemini API Key if you plan to use the live extraction:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Usage

The main entry point is `main.py`.

### 1. Mock Mode (Gold Standard Demo)

To run the pipeline using pre-validated "Gold Standard" extraction data (no API key required):

```bash
python main.py --mock
```

This is the default mode if no API key is found.

### 2. Live Mode (LLM Extraction)

To run the pipeline using the Gemini API for extraction:

```bash
python main.py --live
```

_Note: Ensure valid `GEMINI_API_KEY` is set._

## Output

Artifacts are generated in the `output/` directory:

- `graph.json`: Nodes and Edges with metadata and provenance.
- `graph.mmd`: Mermaid syntax file. You can paste the content into [Mermaid Live Editor](https://mermaid.live/) to visualize.

## Project Structure

- `data/`: Contains input chunks and gold standard extraction data.
- `src/`: Source code.
  - `extraction.py`: Handles LLM interaction (Gemini) and Gold Standard retrieval.
  - `graph_builder.py`: Manages graph state, deduplication, and merging.
  - `mermaid_renderer.py`: Converts graph to Mermaid syntax.
  - `pipeline.py`: Orchestrates the flow.
  - `config.py`: Configuration and Ontology.
