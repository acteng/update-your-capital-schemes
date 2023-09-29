terraform {
  backend "gcs" {
    bucket = "dft-ate-schemes-tf-backend"
    prefix = "schemes"
  }
}

provider "google" {
  project = local.project
}

locals {
  env      = terraform.workspace
  project  = "dft-ate-schemes-${local.env}"
  location = "europe-west1"
}

module "secret_manager" {
  source  = "./secret-manager"
  project = local.project
}

module "cloud_run" {
  source   = "./cloud-run"
  project  = local.project
  location = local.location
  env      = local.env

  depends_on = [module.secret_manager]
}

module "github_action" {
  source                       = "./github-action"
  project                      = local.project
  cloud_run_service_account_id = module.cloud_run.service_account_id
}
