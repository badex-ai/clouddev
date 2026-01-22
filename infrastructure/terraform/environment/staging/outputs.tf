# Staging Environment Outputs
# These outputs expose infrastructure values needed by applications and CI/CD

# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.app_platform.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.app_platform.private_subnet_ids
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.app_platform.public_subnet_ids
}

# EKS Outputs
output "cluster_name" {
  description = "EKS cluster name"
  value       = module.app_platform.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.app_platform.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data for cluster communication"
  value       = module.app_platform.cluster_certificate_authority_data
  sensitive   = true
}

output "oidc_provider_arn" {
  description = "EKS OIDC provider ARN"
  value       = module.app_platform.oidc_provider_arn
}

# RDS Outputs
output "db_instance_endpoint" {
  description = "RDS instance endpoint (hostname:port)"
  value       = module.app_platform.db_instance_endpoint
}

output "db_instance_name" {
  description = "RDS database name"
  value       = module.app_platform.db_instance_name
}

output "db_secret_arn" {
  description = "ARN of the secret containing DB password"
  value       = module.app_platform.db_secret_arn
}

# ElastiCache Outputs
output "elasticache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.app_platform.elasticache_endpoint
}

output "elasticache_port" {
  description = "ElastiCache Redis port"
  value       = module.app_platform.elasticache_port
}

output "redis_auth_token_secret_arn" {
  description = "ARN of the secret containing Redis AUTH token"
  value       = module.app_platform.redis_auth_token_secret_arn
}

# Secrets Manager Outputs
output "backend_secrets_arn" {
  description = "ARN of backend application secrets"
  value       = module.app_platform.backend_secrets_arn
}

output "frontend_secrets_arn" {
  description = "ARN of frontend application secrets"
  value       = module.app_platform.frontend_secrets_arn
}

# IAM Role Outputs (for Kubernetes service accounts)
output "aws_load_balancer_controller_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"
  value       = module.app_platform.aws_load_balancer_controller_role_arn
}

output "external_secrets_role_arn" {
  description = "IAM role ARN for External Secrets Operator"
  value       = module.app_platform.external_secrets_role_arn
}

# Security Group Outputs
output "backend_pod_security_group_id" {
  description = "Security group ID for backend pods"
  value       = module.app_platform.backend_pod_security_group_id
}

output "frontend_pod_security_group_id" {
  description = "Security group ID for frontend pods"
  value       = module.app_platform.frontend_pod_security_group_id
}

# KMS Outputs
output "kms_key_arn" {
  description = "KMS key ARN for EKS encryption"
  value       = module.app_platform.kms_key_arn
}

# Helpful commands
output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --name ${module.app_platform.cluster_name} --region ${var.region}"
}
