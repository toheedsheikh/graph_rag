import argparse
import os
from src.config import LLMConfig
from src.pipeline import Pipeline
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="GraphRAG Assignment Pipeline")
    parser.add_argument("--mock", action="store_true", help="Force Mock Mode (use gold standard data)")
    parser.add_argument("--live", action="store_true", help="Force Live Mode (use Gemini API)")
    
    args = parser.parse_args()
    
    # Logic to determine mode
    # Default is Mock Mode as per config, but CLI can override
    mock_mode = True
    if args.live:
        mock_mode = False
    elif args.mock:
        mock_mode = True
    
    # If live mode, check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not mock_mode and not api_key:
        print("Error: Live mode requested but GEMINI_API_KEY not set.")
        return

    config = LLMConfig(api_key=api_key, mock_mode=mock_mode)
    
    pipeline = Pipeline(config)
    pipeline.run()

if __name__ == "__main__":
    main()
