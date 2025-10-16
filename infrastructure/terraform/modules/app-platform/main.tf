# Main configuration file that brings together all components
# This file serves as the entry point for the app-platform module

# Local values for common tags
locals {
  common_tags = merge(var.tags, {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

# Random password for secure generation
resource "random_password" "master" {
  length  = 16
  special = true

  lifecycle {
    create_before_destroy = true
  }
}
