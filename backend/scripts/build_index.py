import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag.indexer import Indexer
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description="Build ChromaDB index from Genius lyrics")
    
    parser.add_argument(
        "--lyrics-dir",
        type=str,
        required=True,
        help="Path to directory containing Genius JSON files"
    )
    
    parser.add_argument(
        "--collection-name",
        type=str,
        default="lyric_chunks",
        help="Name of ChromaDB collection (default: lyric_chunks)"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset collection before indexing (deletes existing data)"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't recursively search subdirectories"
    )
    
    args = parser.parse_args()
    
    indexer = Indexer(collection_name=args.collection_name, reset=args.reset)
    indexer.index_dir(args.lyrics_dir, recursive=not args.no_recursive)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()