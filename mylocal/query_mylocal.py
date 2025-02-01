import argparse

from mylocal.ai.chat import Neo4jQueryProcessor


def main():
    parser = argparse.ArgumentParser(description="Query the Neo4j document database")
    parser.add_argument("--query", type=str, required=True, help="Query to search for in the documents")
    parser.add_argument("--k", type=int, default=2, help="Number of results to return (default: 2)")

    args = parser.parse_args()

    # Initialize the Neo4jQueryProcessor
    processor = Neo4jQueryProcessor(model_name="openai")

    # Run the query using the processor
    try:
        results = processor.query(args.query)
        print("Query Results:")
        for result in results:
            print(result)
    except Exception as e:
        print(f"An error occurred while querying: {e}")


if __name__ == "__main__":
    main()
