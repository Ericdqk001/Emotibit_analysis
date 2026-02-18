"""Print the folder structure of the INTACT-MCI emotibit data."""

import sys
from pathlib import Path


def print_tree(directory: Path, prefix: str = "", max_depth: int = 4, depth: int = 0):
    """Print directory tree up to max_depth."""
    if depth >= max_depth:
        return

    entries = sorted(directory.iterdir())
    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if e.is_file()]

    for f in files:
        print(f"{prefix}{f.name}")

    for i, d in enumerate(dirs):
        is_last = i == len(dirs) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{d.name}/")
        next_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(d, next_prefix, max_depth, depth + 1)


if __name__ == "__main__":
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path("/Volumes/INT-ACT/INTACT-MCI/emotibit/")
    )

    if not path.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    print(f"{path.name}/")
    print_tree(path)
