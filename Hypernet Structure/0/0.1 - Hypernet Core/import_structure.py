"""
Import Existing Hypernet Structure

Walks the Hypernet Structure folder tree and imports it as nodes and links
into the Hypernet graph store. This makes the existing documentation,
identity files, and planning documents queryable through the API.

Mapping logic:
  Folder "0/0.1 - Hypernet Core"  ->  Node at address "0.0.1" (approx)
  File "README.md" inside a folder ->  Content stored in the node's data

For the initial import, we use a simplified addressing scheme that maps
folder names to addresses where possible, and generates sequential
addresses where the folder name doesn't contain an address.

Usage:
  python import_structure.py [--data-dir data] [--source-dir .]
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from hypernet.address import HypernetAddress
from hypernet.node import Node
from hypernet.link import Link
from hypernet.store import Store


# Maps top-level folder names to Hypernet address categories
CATEGORY_MAP = {
    "0": "0",
    "1 - People": "1",
    "2 - AI Accounts": "2",
    "2 - AI Entities": "2",
    "3 - Businesses": "3",
    "4 - Knowledge": "4",
    "4 -  Knowledge": "4",
    "5 - Objects": "5",
    "5 - People of History": "5",
    "6 - People of History": "6",
    "9 - Aliases": "9",
}

# Pattern to extract address-like numbers from folder names
ADDRESS_PATTERN = re.compile(r'^(\d+(?:\.\d+)*)')
FOLDER_NUM_PATTERN = re.compile(r'^(\d+(?:\.\d+)*)\s*-?\s*(.*)')


def extract_address_from_name(name: str) -> tuple[str | None, str]:
    """
    Try to extract a Hypernet address prefix from a folder/file name.
    Returns (address_prefix_or_None, clean_name).

    Examples:
      "0.1 - Hypernet Core" -> ("0.1", "Hypernet Core")
      "2.1 - Claude Opus (First AI Citizen)" -> ("2.1", "Claude Opus (First AI Citizen)")
      "README.md" -> (None, "README.md")
    """
    match = FOLDER_NUM_PATTERN.match(name)
    if match:
        return match.group(1), match.group(2).strip()
    return None, name


def import_folder(
    store: Store,
    folder_path: Path,
    address_prefix: str,
    parent_address: str | None = None,
    depth: int = 0,
    max_depth: int = 8,
) -> int:
    """
    Recursively import a folder and its contents as nodes.
    Returns count of nodes created.
    """
    if depth > max_depth:
        return 0

    count = 0

    # Create node for this folder
    folder_data = {
        "name": folder_path.name,
        "type": "folder",
        "path": str(folder_path),
    }

    # Check for README.md or similar content files
    for content_file in ["README.md", "node.json", "index.md"]:
        content_path = folder_path / content_file
        if content_path.exists():
            try:
                text = content_path.read_text(encoding="utf-8", errors="replace")
                # Truncate very long files for the data field
                if len(text) > 10000:
                    folder_data["content_preview"] = text[:10000] + "\n... [truncated]"
                else:
                    folder_data["content"] = text
                folder_data["content_file"] = content_file
            except Exception:
                pass

    try:
        ha = HypernetAddress.parse(address_prefix)
        node = Node(
            address=ha,
            data=folder_data,
            source_type="import",
            source_id=f"folder:{folder_path.name}",
        )
        store.put_node(node)
        count += 1

        # Link to parent
        if parent_address:
            try:
                link = Link(
                    from_address=HypernetAddress.parse(parent_address),
                    to_address=ha,
                    link_type="0.6.3",
                    relationship="contains",
                )
                store.put_link(link)
            except ValueError:
                pass  # Skip invalid links
    except ValueError as e:
        print(f"  Warning: Skipping invalid address '{address_prefix}': {e}")
        return 0

    # Process subfolders
    # First pass: collect all explicitly-addressed children to avoid collisions
    if folder_path.is_dir():
        reserved_suffixes: set[str] = set()
        children = sorted(
            [c for c in folder_path.iterdir()
             if not c.name.startswith(".") and c.name != "__pycache__"],
            key=lambda c: c.name,
        )

        for child in children:
            if child.is_dir():
                addr_part, _ = extract_address_from_name(child.name)
                if addr_part:
                    # Track the last segment to avoid collision with sequential numbering
                    if addr_part.startswith(address_prefix + "."):
                        suffix = addr_part[len(address_prefix) + 1:]
                    elif addr_part.startswith(address_prefix):
                        suffix = addr_part[len(address_prefix):]
                    else:
                        suffix = addr_part
                    # Track the first segment of the suffix (e.g., "1" from "1.2.3")
                    first_seg = suffix.split(".")[0] if suffix else ""
                    if first_seg.isdigit():
                        reserved_suffixes.add(int(first_seg))

        # Sequential counter starts above the highest reserved number
        child_counter = max(reserved_suffixes) if reserved_suffixes else 0

        for child in children:
            if child.is_dir():
                addr_part, clean_name = extract_address_from_name(child.name)

                if addr_part:
                    child_address = addr_part
                    # If the extracted address doesn't start with our prefix,
                    # make it relative
                    if not child_address.startswith(address_prefix):
                        child_address = f"{address_prefix}.{addr_part}"
                else:
                    child_counter += 1
                    # Skip any numbers that collide with named folders
                    while child_counter in reserved_suffixes:
                        child_counter += 1
                    child_address = f"{address_prefix}.{child_counter}"

                count += import_folder(
                    store, child, child_address,
                    parent_address=address_prefix,
                    depth=depth + 1,
                    max_depth=max_depth,
                )

            elif child.is_file() and child.suffix in (".md", ".txt", ".py", ".sql", ".json"):
                # Import individual files as leaf nodes
                child_counter += 1
                # Skip any numbers that collide with named folders
                while child_counter in reserved_suffixes:
                    child_counter += 1
                file_address = f"{address_prefix}.{child_counter}"

                file_data = {
                    "name": child.name,
                    "type": "file",
                    "extension": child.suffix,
                    "path": str(child),
                    "size": child.stat().st_size,
                }

                # Read small files
                if child.stat().st_size < 50000:
                    try:
                        file_data["content"] = child.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        pass

                try:
                    file_ha = HypernetAddress.parse(file_address)
                    file_node = Node(
                        address=file_ha,
                        data=file_data,
                        source_type="import",
                        source_id=f"file:{child.name}",
                    )
                    store.put_node(file_node)
                    count += 1

                    # Link file to parent folder
                    link = Link(
                        from_address=ha,
                        to_address=file_ha,
                        link_type="0.6.3",
                        relationship="contains",
                    )
                    store.put_link(link)
                except ValueError:
                    pass

    return count


def import_structure(source_dir: str = ".", data_dir: str = "data") -> dict:
    """
    Import the entire Hypernet Structure into the graph store.
    Returns import statistics.
    """
    source = Path(source_dir).resolve()
    store = Store(data_dir)

    print(f"Importing from: {source}")
    print(f"Storing to: {Path(data_dir).resolve()}")
    print()

    total_nodes = 0

    # Process top-level folders
    for child in sorted(source.iterdir()):
        if child.name.startswith(".") or not child.is_dir():
            continue

        # Map folder name to category
        category = CATEGORY_MAP.get(child.name)

        if category is None:
            # Try extracting address from name
            addr_part, clean_name = extract_address_from_name(child.name)
            if addr_part:
                category = addr_part
            else:
                continue  # Skip unmapped folders

        print(f"[{category}.*] Importing: {child.name}")
        count = import_folder(store, child, category, depth=0)
        print(f"       -> {count} nodes created")
        total_nodes += count

    stats = store.stats()
    print(f"\n=== Import Complete ===")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total links: {stats['total_links']}")
    print(f"Types: {stats['types']}")
    print(f"Owners: {stats['owners']}")

    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import Hypernet Structure into graph store")
    parser.add_argument("--source-dir", default="C:/Hypernet/Hypernet Structure",
                       help="Path to Hypernet Structure folder")
    parser.add_argument("--data-dir", default="C:/Hypernet/Hypernet Structure/0/0.1 - Hypernet Core/data",
                       help="Path to store graph data")
    args = parser.parse_args()

    import_structure(args.source_dir, args.data_dir)
