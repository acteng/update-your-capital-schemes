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
  domain   = "update-your-capital-schemes.activetravelengland.gov.uk"

  config = {
    dev = {
      keep_idle        = false
      basic_auth       = true
      ate_api          = true
      database_backups = false
      monitoring       = false
      domain           = "dev.${local.domain}"
    }
    test = {
      keep_idle        = false
      basic_auth       = true
      ate_api          = false
      database_backups = false
      monitoring       = false
      domain           = "test.${local.domain}"
    }
    prod = {
      keep_idle        = true
      basic_auth       = false
      ate_api          = false
      database_backups = true
      monitoring       = true
      domain           = local.domain
    }
  }
}

data "terraform_remote_state" "docker_repository" {
  backend = "gcs"
  config = {
    bucket = "dft-schemes-common-tf-backend"
    prefix = "docker-repository"
  }
}

data "terraform_remote_state" "schemes_database" {
  backend = "gcs"
  config = {
    bucket = "dft-ate-capitalschemes-common-tf-backend"
    prefix = "schemes-database"
  }
  workspace = local.env
}

data "terraform_remote_state" "identity" {
  backend = "gcs"
  config = {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "identity"
  }
  workspace = local.env
}

data "terraform_remote_state" "ate_api" {
  backend = "gcs"
  config = {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "service"
  }
  workspace = local.env
}

resource "google_project_service" "secret_manager" {
  project = local.project
  service = "secretmanager.googleapis.com"
}

resource "google_project_service" "monitoring" {
  project = local.project
  service = "monitoring.googleapis.com"
}

module "cloud_sql" {
  source           = "./cloud-sql"
  project          = local.project
  region           = local.location
  database_backups = local.config[local.env].database_backups

  depends_on = [google_project_service.secret_manager]
}

module "cloud_run" {
  source                                   = "./cloud-run"
  project                                  = local.project
  region                                   = local.location
  docker_repository_project                = data.terraform_remote_state.docker_repository.outputs.project
  docker_repository_url                    = data.terraform_remote_state.docker_repository.outputs.url
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
  keep_idle                                = local.config[local.env].keep_idle
  basic_auth                               = local.config[local.env].basic_auth
  ate_api_url                              = local.config[local.env].ate_api ? data.terraform_remote_state.ate_api.outputs.url : null
  ate_api_client_id                        = local.config[local.env].ate_api ? data.terraform_remote_state.identity.outputs.update_your_capital_schemes_client_id : null
  ate_api_client_secret                    = local.config[local.env].ate_api ? data.terraform_remote_state.identity.outputs.update_your_capital_schemes_client_secret : null
  ate_api_server_metadata_url              = local.config[local.env].ate_api ? data.terraform_remote_state.identity.outputs.oidc_server_metadata_url : null
  ate_api_audience                         = local.config[local.env].ate_api ? data.terraform_remote_state.identity.outputs.resource_server_identifier : null
  monitoring                               = local.config[local.env].monitoring
  domain                                   = local.config[local.env].domain

  depends_on = [
    google_project_service.secret_manager,
    google_project_service.monitoring
  ]
}

module "web_application_firewall" {
  source = "./web-application-firewall"
}

module "load_balancer" {
  source                 = "./load-balancer"
  region                 = local.location
  domain                 = local.config[local.env].domain
  cloud_run_service_name = module.cloud_run.name
  security_policy_id     = module.web_application_firewall.security_policy_id
}

module "github_action_deploy" {
  source                       = "./github-action-deploy"
  project                      = local.project
  docker_repository_project    = data.terraform_remote_state.docker_repository.outputs.project
  cloud_run_service_account_id = module.cloud_run.service_account_id
}

module "github_action_database" {
  source  = "./github-action-database"
  project = local.project
}
