# dnmining

Explore `ree-and-coal-open-geodatabase.gdb` with GeoPandas in
`geodatabase_explorer.ipynb`.

## Python environment

Requires Python 3.12. Dependencies match the existing working notebook
environment. Poetry manages dependencies only; this project is not a Python package.

Install Poetry separately from the notebook environment by following the
[Poetry installation documentation](https://python-poetry.org/docs/#installation).

To use your existing environment from Git Bash:

```bash
# Use the local Poetry installation created during setup (this terminal only).
alias poetry='./.poetry-tools/Scripts/poetry.exe'
source "/c/Users/antho/.virtualenvs/.venv/Scripts/activate"
poetry install
poetry run python --version
```

On another machine, install Poetry using the documentation above and omit the alias.

In VS Code, select that environment using the notebook's **Select Kernel** menu.

For a new project environment, start from a terminal with no active venv:

```bash
poetry env use 3.12
poetry install
```

Alternatively, install the same direct dependencies without Poetry into an
activated Python 3.12 environment:

```bash
python -m pip install -r requirements.txt
```

When changing dependencies, update both `pyproject.toml` and `requirements.txt`,
then run `poetry lock` and `poetry install`. Commit the resulting `poetry.lock`
to preserve resolved transitive dependency versions.

For gdb folder go to https://edx.netl.doe.gov/dataset/ree-and-coal-open-geodatabase?__no_cache__=True 