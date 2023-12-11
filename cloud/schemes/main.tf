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

module "vpc" {
  source = "./vpc"
}

module "cloud_sql" {
  source                      = "./cloud-sql"
  region                      = local.location
  vpc_id                      = module.vpc.id
  vpc_private_ip_address_name = module.vpc.private_ip_address_name

  depends_on = [
    module.secret_manager,
    module.vpc
  ]
}

module "cloud_run" {
  source                         = "./cloud-run"
  project                        = local.project
  region                         = local.location
  env                            = local.env
  database_uri_secret_id         = module.cloud_sql.database_uri_secret_id
  database_uri_secret_version_id = module.cloud_sql.database_uri_secret_version_id
  vpc_id                         = module.vpc.id

  depends_on = [
    module.secret_manager,
    module.vpc
  ]
}

module "github_action" {
  source                       = "./github-action"
  project                      = local.project
  cloud_run_service_account_id = module.cloud_run.service_account_id
}
