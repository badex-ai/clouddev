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

  # VPC Configuration
  vpc_cidr = "10.0.0.0/16"

  # EKS Configuration
  cluster_version           = "1.31"       # ← ADD THIS LINE
  node_group_instance_types = ["t3.small"] # ← CHANGE from t3.micro to t3.small
  node_group_desired_size   = 2
  node_group_min_size       = 1
  node_group_max_size       = 2

  # RDS Configuration
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  # Tags
  tags = {
    CostCenter = "staging" # ← CHANGE from "development" to "staging"
    Owner      = "dev-team"
  }
}
