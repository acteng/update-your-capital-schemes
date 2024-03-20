# Schemes application infrastructure

This root module contains the Terraform configuration for the Schemes application.

## High level services

* Cloud Run Service
* Cloud SQL Instance
* Secret Manager
* Virtual Private Cloud (VPC)
* GitHub Action Service Account

## Application

The Schemes App runs as a Docker container within a Cloud Run service that sits outside the project VPC. 
The service has an associated service account that has delegated permissions to access application secrets held within 
the Secret Manager instance. The service has no IAM restrictions around who can invoke the service with user 
authentication being handled within the application. The application connections into the Cloud SQL Instance using the 
[Direct VPC egress API](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc), which requires a subnet within the VPC with "at least a few hundred IP addresses 
available" which is configured within the Cloud Run module. Direct VPC access is configured to [only route requests to 
private IPs via the VPC](https://cloud.google.com/run/docs/configuring/vpc-connectors#egress-service) and allow all other traffic to route normally. The Cloud Run service pulls Docker images
from an Artifact Registry instance that exists within a separate project and permissions to access this are provided
to the Cloud Run service agent within the Cloud Run service project.

## Network

The VPC used in the Schemes app is required to enable our Cloud SQL Instance to have a private IP address. The Schemes 
VPC is not configured in [`auto` mode](https://cloud.google.com/vpc/docs/create-modify-vpc-networks#create-auto-network) as this is not advised for production or required in our use case. In order 
to connect the VPC to wider Google Cloud Services the VPC has an allocation of static internal IP addresses covering 
the address range `10.0.0.0/24` this is configured to connect to the `servicenetworking.googleapis.com` API and ensures 
the Cloud SQL instance is delegated a static IP from this range. For the Cloud Run service to connect to the Cloud SQL 
Instance within the VPC, a subnet covering IP addresses `10.1.0.0/24` is created within the Cloud Run module and used 
by the Cloud Run service to configure [Direct VPC egress](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc).

## GitHub Actions

To enable the project to use GitHub Actions for CI a Google service account is created with specific permissions to
allow GitHub actions to authenticate with Google Cloud Services. The service account requires the following permissions:

* roles/iam.serviceAccountTokenCreator, to allow the Google Auth GitHub action to authenticate as the service account
* roles/run.admin, to allow the service account to update the Cloud Run service configuration when deploying
* roles/iam.serviceAccountUser, to act as the Cloud Run service account when deploying a revision of the Cloud Run 
service

The method for authenticating the GitHub Action with the service account is by providing the service account JSON key 
as a GitHub action secret.
