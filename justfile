set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

@setup: venv-setup pre-commit-setup requirements-setup
    echo "Setting up..."

@venv-setup:
    uv venv --clear
    uv sync --all-groups

@pre-commit-setup:
    uv run pre-commit install
    uv run pre-commit autoupdate

@requirements-setup:
    uv export --all-groups --no-hashes  --no-annotate --output-file requirements.txt

@lint:
    uv run ruff format .
    uv run ruff check . --fix
