terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = "staging"
      ManagedBy   = "terraform"
    }
  }
}

module "app_platform" {
  source = "../../modules/app-platform"

  environment  = "staging"
  project_name = var.project_name
  region       = var.region

  # Staging-specific configurations
  vpc_cidr = "10.1.0.0/16"

  # Medium instance types for staging
  node_group_instance_types = ["t3.medium"]
  node_group_desired_size   = 2
  node_group_min_size       = 2
  node_group_max_size       = 4

  # Medium DB for staging
  db_instance_class    = "db.t3.small"
  db_allocated_storage = 50

  tags = {
    CostCenter = "staging"
    Owner      = "platform-team"
  }
}
