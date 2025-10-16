# Data source to get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# Use the first 3 AZs or provided ones
locals {
  azs = length(var.availability_zones) > 0 ? var.availability_zones : slice(data.aws_availability_zones.available.names, 0, 3)
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs              = local.azs
  private_subnets  = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, k)]
  public_subnets   = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 48)]
  database_subnets = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 52)]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  single_nat_gateway = var.environment == "dev" ? true : false

  create_database_subnet_group = true

  # Required for EKS
  public_subnet_tags = {
    "kubernetes.io/cluster/${var.project_name}-${var.environment}" = "shared"
    "kubernetes.io/role/elb"                                       = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.project_name}-${var.environment}" = "shared"
    "kubernetes.io/role/internal-elb"                              = "1"
  }

  tags = merge(var.tags, {
    Environment = var.environment
  })
}
