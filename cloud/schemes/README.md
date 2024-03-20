# Schemes application infrastructure

This root module contains the Terraform configuration for the Schemes application.

## High level services

* Cloud Run Service
* Cloud SQL Instance
* Secret Manager
* GitHub Action Service Account

## Application

The Schemes App runs as a Docker container within a Cloud Run service. The service has an associated service account
that has delegated permissions to access application secrets held within the Secret Manager instance. The service has no
IAM restrictions around who can invoke the service with user authentication being handled within the application. The
application connects to Cloud SQL using [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy).
The Cloud Run service pulls Docker images from an Artifact Registry instance that exists within a separate project and
permissions to access this are provided to the Cloud Run service agent within the Cloud Run service project.

## GitHub Actions

To enable the project to use GitHub Actions for CI a Google service account is created with specific permissions to
allow GitHub actions to authenticate with Google Cloud Services. The service account requires the following permissions:

* roles/iam.serviceAccountTokenCreator, to allow the Google Auth GitHub action to authenticate as the service account
* roles/run.admin, to allow the service account to update the Cloud Run service configuration when deploying
* roles/iam.serviceAccountUser, to act as the Cloud Run service account when deploying a revision of the Cloud Run 
service

The method for authenticating the GitHub Action with the service account is by providing the service account JSON key 
as a GitHub action secret.
