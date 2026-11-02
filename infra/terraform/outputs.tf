output "api_url" {
  description = "Public URL of the deployed API"
  value       = google_cloud_run_v2_service.api.uri
}
