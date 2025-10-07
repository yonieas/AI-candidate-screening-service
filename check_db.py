# check_db.py
import chromadb
import argparse
from config import DB_PATH, COLLECTION_NAME
import json

def inspect_chromadb(filter_source=None, get_all=False):
    """
    Connects to the ChromaDB database and retrieves information about the collection.
    """
    print(f"Connecting to ChromaDB at path: '{DB_PATH}'...")
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"\nERROR: Could not connect to the database or find the collection.")
        print(f"Please make sure you have run 'python ingest.py' first.")
        print(f"Details: {e}")
        return

    # 1. Get the total number of items
    count = collection.count()
    print(f"\n--- Collection Summary ---")
    print(f"Collection Name: '{COLLECTION_NAME}'")
    print(f"Total Items (Chunks) Stored: {count}")
    print("--------------------------\n")

    if count == 0:
        print("The database is empty. Please run the ingestion script.")
        return

    # 2. Handle the different command-line flags
    if get_all:
        print("Fetching all items in the database...")
        results = collection.get() # Get everything
    elif filter_source:
        print(f"Filtering for items where source = '{filter_source}'...")
        results = collection.get(
            where={"source": filter_source}
        )
    else:
        print("Fetching the first 5 items as a sample...")
        results = collection.get(limit=5)

    # 3. Print the results in a readable format
    if not results or not results['ids']:
        print("No items found matching your criteria.")
        return

    print(f"\n--- Found {len(results['ids'])} Item(s) ---")
    for i, item_id in enumerate(results['ids']):
        print(f"\nItem {i+1}:")
        print(f"  ID: {item_id}")

        # Pretty-print metadata
        metadata = results['metadatas'][i]
        print(f"  Metadata: {json.dumps(metadata, indent=4)}")

        # Print a snippet of the document content
        document_content = results['documents'][i]
        snippet = (document_content[:250] + '...') if len(document_content) > 250 else document_content
        print(f"  Document Snippet: \"{snippet}\"")
    print("\n--------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A tool to inspect the contents of the ChromaDB for the AI screening service."
    )
    parser.add_argument(
        '--filter-source',
        type=str,
        help="Filter items by the original source filename (e.g., 'scoring_rubric.pdf')."
    )
    parser.add_argument(
        '--get-all',
        action='store_true',
        help="Get all items in the database. Warning: can be a lot of text."
    )

    args = parser.parse_args()
    inspect_chromadb(filter_source=args.filter_source, get_all=args.get_all)

'''
### How to Use the Script

This script runs from your terminal. Make sure you have activated your virtual environment first (`source venv/bin/activate`).

**1. Get a Quick Summary and Sample**
This is the default. It shows the total count and the first 5 items.
```bash
python check_db.py
```

**2. Filter by a Specific Source PDF**
This is the most useful command. It shows you all the chunks that were created from a single source file, confirming that the ingestion for that file was successful.
```bash
# Replace 'scoring_rubric.pdf' with the filename you want to check
python check_db.py --filter-source scoring_rubric.pdf
```
```bash
python check_db.py --filter-source job_description.pdf

'''