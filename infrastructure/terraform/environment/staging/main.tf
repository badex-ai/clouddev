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
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.7"
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

# Kubernetes provider configuration for EKS
provider "kubernetes" {
  host                   = module.app_platform.cluster_endpoint
  cluster_ca_certificate = base64decode(module.app_platform.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.app_platform.cluster_name]
  }
}

# Helm provider configuration for EKS
provider "helm" {
  kubernetes = {
    host                   = module.app_platform.cluster_endpoint
    cluster_ca_certificate = base64decode(module.app_platform.cluster_certificate_authority_data)

    exec = {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.app_platform.cluster_name]
    }
  }
}

module "app_platform" {
  source = "../../modules/app-platform"

  environment  = "staging"
  project_name = var.project_name
  region       = var.region

  # VPC Configuration
  vpc_cidr = "10.1.0.0/16"

  # EKS Configuration
  cluster_version           = "1.31"
  node_group_instance_types = ["t3.small", "t3.medium"]  # Multiple types for Spot availability
  node_group_capacity_type  = "SPOT"                     # Use Spot instances (60-70% cheaper)
  node_group_desired_size   = 1                          # Single node for staging
  node_group_min_size       = 1
  node_group_max_size       = 2

  # RDS Configuration
  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20

  # Alarms
  alarm_email = var.alarm_email

  # Application Secrets (passed via staging.tfvars)
  auth0_client_secret     = var.auth0_client_secret
  auth0_m2m_client_secret = var.auth0_m2m_client_secret
  auth0_secret            = var.auth0_secret
  brevo_api_key           = var.brevo_api_key
  redis_password          = var.redis_password

  # Tags
  tags = {
    CostCenter = "staging"
    Owner      = "dev-team"
  }
}
