"""
Add YAML frontmatter to Markdown files in the Hypernet archive.

Usage:
  python add_frontmatter.py                       # Dry run (default)
  python add_frontmatter.py --apply                # Actually modify files
  python add_frontmatter.py --path "2 - AI Accounts"  # Only process one directory
  python add_frontmatter.py --verbose              # Show all metadata inferred

This script:
1. Walks the archive directory tree
2. Finds all .md files
3. Checks if they already have YAML frontmatter
4. Infers metadata (HA, creator, type) from the file's path
5. Adds standard frontmatter if not present

Run with --apply to actually modify files. Without it, shows what would be done.
"""

import argparse
import sys
from pathlib import Path

# Add the hypernet package to path
sys.path.insert(0, str(Path(__file__).parent))

from hypernet.frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path


def main():
    parser = argparse.ArgumentParser(
        description="Add YAML frontmatter to Markdown files in the Hypernet archive"
    )
    parser.add_argument(
        "--archive", default="../..",
        help="Path to the Hypernet Structure root (default: ../..)"
    )
    parser.add_argument(
        "--path", default=None,
        help="Only process files under this subdirectory"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually modify files (without this flag, it's a dry run)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show inferred metadata for each file"
    )
    parser.add_argument(
        "--skip-existing", action="store_true", default=True,
        help="Skip files that already have frontmatter (default: True)"
    )
    args = parser.parse_args()

    archive_root = Path(args.archive).resolve()
    search_root = archive_root / args.path if args.path else archive_root

    if not search_root.exists():
        print(f"Error: Path not found: {search_root}")
        sys.exit(1)

    print(f"Archive root: {archive_root}")
    print(f"Search path:  {search_root}")
    print(f"Mode:         {'APPLY' if args.apply else 'DRY RUN'}")
    print()

    # Find all .md files
    md_files = sorted(search_root.rglob("*.md"))

    # Filter out hidden directories and node_modules
    md_files = [
        f for f in md_files
        if not any(part.startswith(".") for part in f.relative_to(archive_root).parts)
        and "node_modules" not in str(f)
    ]

    total = len(md_files)
    skipped = 0
    would_add = 0
    added = 0
    errors = 0

    for filepath in md_files:
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ERROR reading {filepath}: {e}")
            errors += 1
            continue

        # Check for existing frontmatter
        existing_meta, body = parse_frontmatter(content)
        if existing_meta and args.skip_existing:
            skipped += 1
            if args.verbose:
                relpath = filepath.relative_to(archive_root)
                print(f"  SKIP (has frontmatter): {relpath}")
            continue

        # Infer metadata
        metadata = infer_metadata_from_path(filepath, archive_root)

        relpath = filepath.relative_to(archive_root)

        if args.verbose:
            print(f"  {relpath}")
            print(f"    ha: {metadata['ha']}")
            print(f"    creator: {metadata['creator']}")
            print(f"    object_type: {metadata['object_type']}")
            print()
        else:
            status = "ADD" if args.apply else "WOULD ADD"
            print(f"  [{status}] {relpath}  ->  ha={metadata['ha']}, creator={metadata['creator']}")

        if args.apply:
            new_content = add_frontmatter(content, metadata)
            filepath.write_text(new_content, encoding="utf-8")
            added += 1
        else:
            would_add += 1

    print()
    print("=" * 50)
    print(f"Total .md files found: {total}")
    print(f"Already have frontmatter: {skipped}")
    if args.apply:
        print(f"Frontmatter added: {added}")
    else:
        print(f"Would add frontmatter: {would_add}")
    print(f"Errors: {errors}")

    if not args.apply and would_add > 0:
        print()
        print("Run with --apply to actually modify files.")


if __name__ == "__main__":
    main()
