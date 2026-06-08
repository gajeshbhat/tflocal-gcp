terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

# These values are placeholders for local use; tflocal-gcp injects the localgcp
# endpoints and a dummy access token at runtime, so no real credentials or
# project are required.
provider "google" {
  project = "local-project"
  region  = "us-central1"
}

resource "google_storage_bucket" "demo" {
  name     = "my-local-bucket"
  location = "US"

  force_destroy = true
}
