terraform {
  backend "gcs" {
    bucket = "dft-schemes-common-tf-backend"
    prefix = "schemes"
  }
}

provider "google" {
  project = local.project
}

locals {
  env      = terraform.workspace
  project  = "dft-schemes-${local.env}"
  location = "europe-west1"
}

module "secret_manager" {
  source  = "./secret-manager"
  project = local.project
}

module "cloud_sql" {
  source  = "./cloud-sql"
  project = local.project
  region  = local.location

  depends_on = [
    module.secret_manager
  ]
}

module "cloud_run" {
  source                   = "./cloud-run"
  project                  = local.project
  region                   = local.location
  env                      = local.env
  database_connection_name = module.cloud_sql.connection_name
  database_name            = module.cloud_sql.name
  database_username        = module.cloud_sql.username
  database_password        = module.cloud_sql.password

  depends_on = [
    module.secret_manager
  ]
}

module "github_action" {
  source                       = "./github-action"
  project                      = local.project
  cloud_run_service_account_id = module.cloud_run.service_account_id
}
