resource "google_sql_database_instance" "main" {
  name   = "schemes"
  region = var.region

  database_version = "POSTGRES_15"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled       = false
      private_network    = var.vpc_id
      allocated_ip_range = var.vpc_private_ip_address_name
    }
  }
}

resource "google_sql_database" "schemes" {
  name     = "schemes"
  instance = google_sql_database_instance.main.name
}

resource "google_secret_manager_secret" "database_uri" {
  secret_id = "database-uri"

  replication {
    auto {
    }
  }
}

resource "random_password" "schemes" {
  length  = 32
  special = false
}

resource "google_sql_user" "schemes" {
  name     = "schemes"
  instance = google_sql_database_instance.main.name

  password = random_password.schemes.result
}

resource "google_secret_manager_secret_version" "database_uri" {
  secret = google_secret_manager_secret.database_uri.id
  secret_data = join("", [
    "postgresql+pg8000://",
    google_sql_user.schemes.name,
    ":",
    random_password.schemes.result,
    "@",
    google_sql_database_instance.main.private_ip_address,
    "/",
    google_sql_database.schemes.name
  ])
}
