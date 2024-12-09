import argparse
from whoosh import index
from whoosh.qparser import QueryParser

# Base URL of the Confluence instance
BASE_CONFLUENCE_URL = (
    "https://wiki.htw-berlin.de/confluence/pages/viewpage.action?pageId="
)

# Directory of the index
INDEX_DIR = "lucene_index"


def search_index(query_str):
    # Open the existing Whoosh index
    if not index.exists_in(INDEX_DIR):
        print("Index does not exist. Please create it first.")
        return

    idx = index.open_dir(INDEX_DIR)

    # Parse the query and search
    with idx.searcher() as searcher:
        query = QueryParser("content", idx.schema).parse(query_str)
        results = searcher.search(query, limit=10)

        if not results:
            print("No results found.")
        else:
            for result in results:
                page_id = result["page_id"]
                title = result["title"]
                page_url = f"{BASE_CONFLUENCE_URL}{page_id}"
                print(f"Title: {title}")
                print(f"URL: {page_url}")
                print("-" * 40)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Search the Whoosh index.")
    parser.add_argument("query", type=str, help="Search query string")
    args = parser.parse_args()

    # Perform the search
    search_index(args.query)


if __name__ == "__main__":
    main()
