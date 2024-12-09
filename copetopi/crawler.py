import os
import requests
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer

# Set up constants
BASE_URL = "https://wiki.htw-berlin.de/confluence/rest/api"
OUTPUT_DIR = "lucene_index"


# Define Whoosh schema for indexing
def create_schema():
    return Schema(
        page_id=ID(stored=True, unique=True),
        title=TEXT(stored=True),
        content=TEXT(stored=False, analyzer=StemmingAnalyzer()),
    )


# Initialize Whoosh index
def initialize_index(output_dir, schema):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        return index.create_in(output_dir, schema)
    return index.open_dir(output_dir)


# Fetch all global (non-personal) spaces
def fetch_spaces():
    response = requests.get(
        f"{BASE_URL}/space", params={"type": "global", "limit": 100}
    )
    response.raise_for_status()
    return response.json().get("results", [])


# Fetch all pages in a space
def fetch_pages(space_key):
    pages = []
    start = 0
    while True:
        response = requests.get(
            f"{BASE_URL}/content",
            params={"type": "page", "spaceKey": space_key, "start": start, "limit": 50},
        )
        response.raise_for_status()
        data = response.json()
        pages.extend(data.get("results", []))
        if not data.get("_links", {}).get("next"):
            break
        start += 50
    return pages


# Fetch page content
def fetch_page_content(page_id):
    response = requests.get(
        f"{BASE_URL}/content/{page_id}", params={"expand": "body.storage"}
    )
    response.raise_for_status()
    return response.json()


# Index pages
def index_pages(writer, pages):
    for page in pages:
        page_id = page["id"]
        title = page["title"]
        content = fetch_page_content(page_id)["body"]["storage"]["value"]
        writer.add_document(page_id=page_id, title=title, content=content)


# Main script
def main():
    schema = create_schema()
    idx = initialize_index(OUTPUT_DIR, schema)
    with idx.writer() as writer:
        spaces = fetch_spaces()
        for space in spaces:
            print(f"Indexing space: {space['name']}...")
            space_key = space["key"]
            pages = fetch_pages(space_key)
            index_pages(writer, pages)
    print("Indexing completed.")


if __name__ == "__main__":
    main()
