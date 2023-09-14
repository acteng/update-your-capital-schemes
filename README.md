# Schemes

## Running locally

1. Create a virtual environment:

    ```bash
    python3 -m venv --prompt . .venv
    ```

1. Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

1. Install the dependencies:

    ```bash
    pip install -e .
    ```

1. Run the server:

    ```bash
    flask run
    ```

1. Open http://127.0.0.1:5000

## Running tests

To run the integration tests:

```bash
pytest
```
