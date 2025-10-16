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
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

module "app_platform" {
  source = "../../modules/app-platform"

  environment  = "prod"
  project_name = var.project_name
  region       = var.region

  # Production-specific configurations  
  vpc_cidr = "10.2.0.0/16"

  # Larger instance types for production
  node_group_instance_types = ["t3.meduim"]
  node_group_desired_size   = 3
  node_group_min_size       = 2
  node_group_max_size       = 10

  # Production DB configuration
  db_instance_class    = "db.t3.medium"
  db_allocated_storage = 100

  tags = {
    CostCenter = "production"
    Owner      = "platform-team"
    Backup     = "required"
  }
}
