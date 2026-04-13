from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge


async def search_graph(
    client: Graphiti,
    query: str,
    group_ids: list[str] | None = None,
    num_results: int = 10,
) -> list[EntityEdge]:
    """Search the knowledge graph and return relevant edges."""
    results = await client.search(
        query=query,
        group_ids=group_ids,
        num_results=num_results,
    )
    return results


def format_context(edges: list[EntityEdge]) -> str:
    """Format retrieved edges into a context string for the LLM."""
    if not edges:
        return "No relevant information found in the knowledge graph."

    facts = []
    for i, edge in enumerate(edges, 1):
        fact = f"{i}. {edge.fact}"
        facts.append(fact)

    return "Relevant facts from the knowledge graph:\n" + "\n".join(facts)


async def retrieve_context(
    client: Graphiti,
    query: str,
    group_ids: list[str] | None = None,
    num_results: int = 10,
) -> str:
    """Search the graph and return formatted context string."""
    edges = await search_graph(client, query, group_ids, num_results)
    return format_context(edges)
