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

  schemes_database = {
    env = "test"
  }
}

data "terraform_remote_state" "schemes_database" {
  backend = "gcs"
  config = {
    bucket = "dft-ate-capitalschemes-common-tf-backend"
    prefix = "schemes-database"
  }
  workspace = local.schemes_database.env
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
  source                                   = "./cloud-run"
  project                                  = local.project
  region                                   = local.location
  env                                      = local.env
  database_connection_name                 = module.cloud_sql.connection_name
  database_name                            = module.cloud_sql.name
  database_username                        = module.cloud_sql.username
  database_password                        = module.cloud_sql.password
  capital_schemes_database_project         = data.terraform_remote_state.schemes_database.outputs.project
  capital_schemes_database_connection_name = data.terraform_remote_state.schemes_database.outputs.connection_name
  capital_schemes_database_name            = data.terraform_remote_state.schemes_database.outputs.name
  capital_schemes_database_username        = data.terraform_remote_state.schemes_database.outputs.username
  capital_schemes_database_password        = data.terraform_remote_state.schemes_database.outputs.password

  depends_on = [
    module.secret_manager
  ]
}

module "github_action_deploy" {
  source                       = "./github-action-deploy"
  project                      = local.project
  cloud_run_service_account_id = module.cloud_run.service_account_id
}

module "github_action_database" {
  source  = "./github-action-database"
  project = local.project
}

moved {
  from = module.github_action
  to   = module.github_action_deploy
}
