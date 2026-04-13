import os
from datetime import datetime

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType


async def ingest_text(
    client: Graphiti,
    text: str,
    name: str,
    source_description: str = "manual text input",
    group_id: str = "default",
    reference_time: datetime | None = None,
) -> None:
    """Ingest a single text block into the knowledge graph."""
    if reference_time is None:
        reference_time = datetime.now()

    result = await client.add_episode(
        name=name,
        episode_body=text,
        source_description=source_description,
        reference_time=reference_time,
        source=EpisodeType.text,
        group_id=group_id,
    )
    print(f"Ingested episode: {name} ({len(result.nodes)} nodes, {len(result.edges)} edges)")
    return result


async def ingest_file(
    client: Graphiti,
    file_path: str,
    group_id: str = "default",
    source_description: str | None = None,
) -> None:
    """Read a text file and ingest its content into the knowledge graph."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    name = os.path.basename(file_path)
    if source_description is None:
        source_description = f"file: {name}"

    return await ingest_text(
        client=client,
        text=content,
        name=name,
        source_description=source_description,
        group_id=group_id,
    )


async def ingest_directory(
    client: Graphiti,
    dir_path: str,
    group_id: str = "default",
    extensions: tuple[str, ...] = (".txt", ".md"),
) -> None:
    """Ingest all matching files from a directory."""
    files = sorted(
        f
        for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
        and f.endswith(extensions)
    )

    if not files:
        print(f"No files with extensions {extensions} found in {dir_path}")
        return

    print(f"Found {len(files)} files to ingest...")
    for filename in files:
        filepath = os.path.join(dir_path, filename)
        await ingest_file(client, filepath, group_id=group_id)

    print("Ingestion complete.")
