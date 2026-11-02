terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# APIs this project needs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

# Docker image registry
resource "google_artifact_registry_repository" "docqa" {
  location      = var.region
  repository_id = "docqa"
  format        = "DOCKER"
  depends_on    = [google_project_service.services]
}

# The API, running on Cloud Run (scales to zero, so it is free when idle)
resource "google_cloud_run_v2_service" "api" {
  name                = "docqa-api"
  location            = var.region
  deletion_protection = false

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    containers {
      image = var.image
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }
      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }
      env {
        name  = "LLM_BASE_URL"
        value = var.llm_base_url
      }
      env {
        name  = "LLM_API_KEY"
        value = var.llm_api_key
      }
      env {
        name  = "LLM_MODEL"
        value = var.llm_model
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Allow public (unauthenticated) access to the API
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.api.name
  location = google_cloud_run_v2_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
