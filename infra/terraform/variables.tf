variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "asia-south1"
}

variable "image" {
  description = "Full image path, e.g. asia-south1-docker.pkg.dev/PROJECT/docqa/api:v1"
  type        = string
}

variable "database_url" {
  description = "Postgres connection string with pgvector (e.g. from Neon free tier)"
  type        = string
  sensitive   = true
}

variable "llm_base_url" {
  type    = string
  default = "https://api.groq.com/openai/v1"
}

variable "llm_api_key" {
  type      = string
  sensitive = true
}

variable "llm_model" {
  type    = string
  default = "llama-3.1-8b-instant"
}
