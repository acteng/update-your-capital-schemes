# Schemes

[![CI](https://github.com/acteng/schemes/actions/workflows/ci.yml/badge.svg)](https://github.com/acteng/schemes/actions/workflows/ci.yml)

## Prerequisites

1. Install Python 3.12
1. Install Node 20
1. Install Docker and Compose plugin
1. Install Google Cloud CLI and authenticate using ADCs:
   ```bash
   gcloud auth application-default login
   ```
1. Install Terraform 1.6
1. Install [Bitwarden CLI](https://bitwarden.com/help/cli/#download-and-install)

## Configure the app

Configure the application's environment variables with the localhost secrets:

```bash
bw get notes "Schemes Secrets (Localhost)" > .env
```

The application can also be configured with the following environment variables:

| Name                             | Value                                                                                       |
|----------------------------------|---------------------------------------------------------------------------------------------|
| FLASK_ENV                        | Application environment name (`dev` / `test`)                                               |
| FLASK_SQLALCHEMY_DATABASE_URI    | SQLAlchemy database URI                                                                     |
| FLASK_SECRET_KEY                 | Flask session [secret key](https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions) |
| FLASK_BASIC_AUTH_USERNAME        | HTTP Basic Auth username                                                                    |
| FLASK_BASIC_AUTH_PASSWORD        | HTTP Basic Auth password                                                                    |
| FLASK_API_KEY                    | API key (unset to disable)                                                                  |
| FLASK_GOVUK_CLIENT_ID            | OIDC client id                                                                              |
| FLASK_GOVUK_CLIENT_SECRET        | OIDC client secret                                                                          |
| FLASK_GOVUK_SERVER_METADATA_URL  | OIDC discovery endpoint                                                                     |
| FLASK_GOVUK_TOKEN_ENDPOINT       | OIDC token endpoint                                                                         |
| FLASK_GOVUK_PROFILE_URL          | OIDC profile URL                                                                            |
| FLASK_GOVUK_END_SESSION_ENDPOINT | OIDC end session endpoint                                                                   |

## Running locally

1. Create a virtual environment:

    ```bash
    python3.12 -m venv --prompt . --upgrade-deps .venv
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
    make run
    ```

1. Open http://127.0.0.1:5000

## Running locally using Docker

To run the server as a container using an in-memory SQLite database:

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
   docker run --rm -it -p 5000:5000 --env-file ./.env schemes
   ```
   
1. Open http://127.0.0.1:5000

The server can also be run on a different port by specifying the `PORT` environment variable:

```bash
docker run --rm -it -e PORT=8000 -p 8000:8000 --env-file ./.env schemes
```

## Running locally using Compose

To run the server as a container using a PostgreSQL database:

1. Build the web assets:

   ```bash
   npm install && npm run build
   ```

1. Run the services:

   ```bash
   docker compose up
   ```
   
1. Open http://127.0.0.1:5000

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

## Provisioning infrastructure

### Provision the Terraform backend

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

### Provision the Docker repository

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

### Provision the application

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

1. This will fail due to missing secrets. Now that the Secret Manager service has been enabled, create the secrets then repeat the previous step:

   ```bash
   bw get notes "Schemes Secrets ($ENVIRONMENT)" | sh
   ```

1. Obtain the Cloud Run service account private key:

   ```bash
   terraform output -raw github_action_private_key
   ```
   
1. [Set the GitHub Actions repository secret](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) `GCP_CREDENTIALS_DEPLOY_$ENVIRONMENT` to the private key

1. Open the output `url`

### Redeploying the service

To manually redeploy the Cloud Run service using the latest image in the Docker repository:

```bash
gcloud run deploy schemes \
    --project dft-schemes-$ENVIRONMENT \
    --region europe-west1 \
    --image europe-west1-docker.pkg.dev/dft-schemes-common/docker/schemes
```

## Authentication

We have [registered](https://docs.sign-in.service.gov.uk/before-integrating/manage-your-service-s-configuration/#register-your-service-to-use-gov-uk-one-login) the following two services with [GOV.UK One Login](https://www.sign-in.service.gov.uk/):

### Dev

* Service name: ATE Schemes (Dev)
* Service redirect URLs: https://schemes-a552yllyya-ew.a.run.app/auth, https://schemes-ijnazoz5mq-ew.a.run.app/auth, http://127.0.0.1:5000/auth
* Service contact email address: mark.hobson@activetravelengland.gov.uk
* Scopes: openid email
* Public key: (see "Schemes GOV.UK One Login Public Key (Dev)" in Bitwarden)
* Logout URLs: https://schemes-a552yllyya-ew.a.run.app/, https://schemes-ijnazoz5mq-ew.a.run.app/, http://127.0.0.1:5000/
* Sector identifier URI: https://schemes-ijnazoz5mq-ew.a.run.app/

### Test

* Service name: ATE Schemes (Test)
* Service redirect URLs: https://schemes-d7yho5f3pa-ew.a.run.app/auth, https://schemes-dcmtqc7uca-ew.a.run.app/auth
* Service contact email address: mark.hobson@activetravelengland.gov.uk
* Scopes: openid email
* Public key: (see "Schemes GOV.UK One Login Public Key (Test)" in Bitwarden)
* Logout URLs: https://schemes-d7yho5f3pa-ew.a.run.app/, https://schemes-dcmtqc7uca-ew.a.run.app/
* Sector identifier URI: https://schemes-dcmtqc7uca-ew.a.run.app/
