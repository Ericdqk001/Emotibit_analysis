from pathlib import Path


def print_folder_structure(folder_path, max_depth: int | None = None) -> str:
    """Print the folder structure as a tree-like string.

    Args:
        folder_path: Path to the folder to print
        max_depth: Maximum depth to traverse (None for unlimited)

    Returns:
        String representation of the folder structure
    """
    path = Path(folder_path)

    if not path.exists():
        return f"Error: Path '{folder_path}' does not exist"

    if not path.is_dir():
        return f"Error: Path '{folder_path}' is not a directory"

    lines = [str(path)]

    def _build_tree(current_path: Path, prefix: str = "", depth: int = 0) -> None:
        """Recursively build the tree structure."""
        if max_depth is not None and depth >= max_depth:
            return

        try:
            items = sorted(
                current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)
            )
        except PermissionError:
            return

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir():
                extension = "    " if is_last else "│   "
                _build_tree(item, prefix + extension, depth + 1)

    _build_tree(path)
    return "\n".join(lines)


if __name__ == "__main__":
    data_store_path = Path("/", "Volumes", "INT-ACT")
    intact_cs2_path = Path(data_store_path, "surveys")

    result = print_folder_structure(intact_cs2_path)
    print(result)
