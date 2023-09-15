# Schemes

[![CI](https://github.com/acteng/schemes/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/schemes/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.10
1. Install Google Cloud CLI and authenticate using ADCs:
   ```bash
   gcloud auth application-default login
   ```
1. Install Terraform 1.5

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
    flask --app schemes run
    ```

1. Open http://127.0.0.1:5000

## Running locally as a container

1. Build the Docker image:

   ```bash
   docker build -t schemes .
   ```
   
1. Run the Docker image:

   ```bash
   docker run --rm -it -p 5000:5000 schemes
   ```
   
1. Open http://127.0.0.1:5000

The server can also be run on a different port by specifying the `PORT` environment variable:

```bash
docker run --rm -it -e PORT=8000 -p 8000:8000 schemes
```

## Running tests

1. Install the dev dependencies:

    ```bash
    pip install -e .[dev]
    ```

1. Install the browsers:

   ```bash
   playwright install chromium
   ```

1. Run the tests:
   
   ```bash
   pytest
   ```

# Provisioning infrastructure

## Provision the Terraform backend

1. Change directory:

   ```bash
   cd cloud/tf-backend
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

## Provision the Docker repository

1. Change directory:

   ```bash
   cd cloud/docker-repository
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Obtain the Docker repository service account private key:

   ```bash
   terraform output -raw github_action_private_key
   ```
   
1. [Set the GitHub Actions repository secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) `GCP_CREDENTIALS` to the private key

## Provision the application

1. Change directory:

   ```bash
   cd cloud/schemes
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. Open the output `uri`
