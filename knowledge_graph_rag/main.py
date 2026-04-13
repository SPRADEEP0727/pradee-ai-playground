import asyncio
import argparse

from src.graph_utils import get_graphiti_client, close_client, clear_graph
from src.ingestion import ingest_file, ingest_directory
from src.retrieval import retrieve_context
from src.generation import generate_response


async def ingest(args):
    """Ingest documents into the knowledge graph."""
    client = await get_graphiti_client()
    try:
        if args.file:
            await ingest_file(client, args.file, group_id=args.group)
        elif args.dir:
            await ingest_directory(client, args.dir, group_id=args.group)
        else:
            print("Provide --file or --dir to ingest.")
    finally:
        await close_client(client)


async def query(args):
    """Query the knowledge graph and generate a response."""
    client = await get_graphiti_client()
    try:
        context = await retrieve_context(
            client, args.query, group_ids=[args.group], num_results=args.num_results
        )
        print(f"\n--- Retrieved Context ---\n{context}\n")

        answer = await generate_response(args.query, context)
        print(f"--- Answer ---\n{answer}\n")
    finally:
        await close_client(client)


async def interactive(args):
    """Interactive query loop."""
    client = await get_graphiti_client()
    try:
        print("Knowledge Graph RAG - Interactive Mode")
        print("Type 'quit' to exit.\n")
        while True:
            user_query = input("Query: ").strip()
            if user_query.lower() in ("quit", "exit", "q"):
                break
            if not user_query:
                continue

            context = await retrieve_context(
                client, user_query, group_ids=[args.group], num_results=args.num_results
            )
            print(f"\n{context}\n")

            answer = await generate_response(user_query, context)
            print(f"Answer: {answer}\n")
    finally:
        await close_client(client)


async def reset(args):
    """Clear all data from the graph."""
    client = await get_graphiti_client()
    try:
        await clear_graph(client)
    finally:
        await close_client(client)


def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph RAG System")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("--file", help="Path to a single file to ingest")
    ingest_parser.add_argument("--dir", help="Path to a directory to ingest")
    ingest_parser.add_argument("--group", default="default", help="Group ID for graph partitioning")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the knowledge graph")
    query_parser.add_argument("query", help="The question to ask")
    query_parser.add_argument("--group", default="default", help="Group ID to search")
    query_parser.add_argument("--num-results", type=int, default=10, help="Number of results")

    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Interactive query mode")
    interactive_parser.add_argument("--group", default="default", help="Group ID to search")
    interactive_parser.add_argument("--num-results", type=int, default=10, help="Number of results")

    # Reset command
    subparsers.add_parser("reset", help="Clear all graph data")

    args = parser.parse_args()

    commands = {
        "ingest": ingest,
        "query": query,
        "interactive": interactive,
        "reset": reset,
    }
    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()
