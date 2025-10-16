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
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

module "app_platform" {
  source = "../../modules/app-platform"

  environment  = "dev"
  project_name = var.project_name
  region       = var.region

  # oidc_provider_arn = module.eks.oidc_provider_arn 

  # Dev-specific configurations
  vpc_cidr = "10.0.0.0/16"

  # Smaller instance types for dev
  node_group_instance_types = ["t3.micro"]
  node_group_desired_size   = 2
  node_group_min_size       = 1
  node_group_max_size       = 3

  # Smaller DB for dev
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  tags = {
    CostCenter = "development"
    Owner      = "dev-team"
  }
}
