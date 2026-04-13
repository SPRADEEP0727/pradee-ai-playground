from graphiti_core import Graphiti
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


async def get_graphiti_client() -> Graphiti:
    """Create and initialize a Graphiti client with Neo4j connection."""
    client = Graphiti(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
    )
    await client.build_indices_and_constraints()
    return client


async def close_client(client: Graphiti):
    """Gracefully close the Graphiti client."""
    await client.close()


async def clear_graph(client: Graphiti):
    """Remove all data from the graph. Use with caution."""
    driver = client.driver
    await driver.execute_query("MATCH (n) DETACH DELETE n")
    print("Graph cleared.")
