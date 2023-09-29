# Schemes

[![CI](https://github.com/acteng/schemes/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/schemes/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.10
1. Install Node 18
1. Install Google Cloud CLI and authenticate using ADCs:
   ```bash
   gcloud auth application-default login
   ```
1. Install Terraform 1.5

## Configure the app

1. Generate a Flask secret key:

    ```bash
    echo "FLASK_SECRET_KEY=$(openssl rand -hex 32)" > .env
    ```

1. Add the 'Schemes GOV.UK One Login Private Key (Dev)' from Bitwarden to `.env`:

    ```
    FLASK_GOVUK_CLIENT_SECRET="-----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----"
    ```

## Running locally

1. Create a virtual environment:

    ```bash
    python3 -m venv --prompt . .venv
    ```

1. Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

1. Build the web assets:

   ```bash
   npm install && npm run build
   ```

1. Install the dependencies:

    ```bash
    pip install -e .[dev]
    ```

1. Run the server:

    ```bash
    flask --app schemes run
    ```

1. Open http://127.0.0.1:5000

## Running locally as a container

1. Build the web assets:

   ```bash
   npm install && npm run build
   ```

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

## Running formatters and linters

1. Install the dependencies:

    ```bash
    pip install -e .[dev]
    ```

1. Run the formatters:

   ```bash
   make format
   ```

1. Run the linters:

   ```bash
   make lint
   ```
   
## Running tests

1. Install the dependencies:

    ```bash
    pip install -e .[dev]
    ```

1. Install the browsers:

   ```bash
   playwright install chromium
   ```

1. Run the tests:
   
   ```bash
   make test
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
   
1. [Set the GitHub Actions repository secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) `GCP_CREDENTIALS_CI` to the private key

## Provision the application

For each environment required (dev, test, prod):

1. Change directory:

   ```bash
   cd cloud/schemes
   ```

1. Initialise Terraform:

   ```bash
   terraform init
   ```

1. Create a Terraform workspace for the environment:

   ```bash
   terraform workspace new $ENVIRONMENT
   ```

1. Apply the changes:

   ```bash
   terraform apply
   ```

1. This will fail due to missing secrets. Find the secure note in the password manager called `Schemes Secrets ($ENVIRONMENT)`
and execute the script. Then repeat the previous step.

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_private_key
   ```
   
1. [Set the GitHub Actions repository secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) `GCP_CREDENTIALS_DEPLOY_$ENVIRONMENT` to the private key

1. Open the output `url`

## Authentication

We have [registered](https://docs.sign-in.service.gov.uk/integrate-with-integration-environment/) the following two services with [GOV.UK One Login](https://www.sign-in.service.gov.uk/):

### Dev

* Service name: ATE Schemes (Dev)
* Service redirect URLs: https://schemes-ijnazoz5mq-ew.a.run.app/auth, http://127.0.0.1:5000/auth
* Service contact email address: mark.hobson@activetravelengland.gov.uk
* Scopes: openid email
* Public key: (see "Schemes GOV.UK One Login Public Key (Dev)" in Bitwarden)
* Logout URL: https://schemes-ijnazoz5mq-ew.a.run.app/, http://127.0.0.1:5000/
* Sector identifier URI: https://schemes-ijnazoz5mq-ew.a.run.app/

### Test

* Service name: ATE Schemes (Test)
* Service redirect URLs: https://schemes-dcmtqc7uca-ew.a.run.app/auth
* Service contact email address: mark.hobson@activetravelengland.gov.uk
* Scopes: openid email
* Public key: (see "Schemes GOV.UK One Login Public Key (Test)" in Bitwarden)
* Logout URL: https://schemes-dcmtqc7uca-ew.a.run.app/
* Sector identifier URI: https://schemes-dcmtqc7uca-ew.a.run.app/
