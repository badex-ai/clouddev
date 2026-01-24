output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnets
}

# EKS outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}


output "cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

# output "cluster_certificate_authority_data" {
#   description = "EKS cluster certificate authority data"
#   value       = module.eks.cluster_certificate_authority_data
# }

output "cluster_oidc_issuer_url" {
  description = "EKS cluster OIDC issuer URL"
  value       = module.eks.cluster_oidc_issuer_url
}

# output "oidc_provider_arn" {
#   description = "EKS OIDC provider ARN"
#   value       = module.eks.oidc_provider_arn
# }

output "node_groups" {
  description = "EKS node groups"
  value       = module.eks.eks_managed_node_groups
}

output "aws_load_balancer_controller_role_arn" {
  description = "AWS Load Balancer Controller IAM role ARN"
  value       = aws_iam_role.aws_load_balancer_controller.arn
}


output "container_insights_enabled" {
  description = "Whether Container Insights is enabled"
  value       = var.enable_cloudwatch_insights
}

output "application_signals_enabled" {
  description = "Whether Application Signals is enabled"
  value       = var.enable_application_signals
}


output "argocd_initial_password_command" {
  description = "Command to get ArgoCD initial admin password"
  value       = "kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"

}

# RDS outputs
output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = module.rds.db_instance_port
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = module.rds.db_instance_identifier
}

output "db_instance_name" {
  description = "RDS database name"
  value       = module.rds.db_instance_name
}

output "db_secret_arn" {
  description = "RDS password secret ARN"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "db_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}







output "kms_key_arn" {
  description = "EKS cluster KMS key ARN"
  value       = aws_kms_key.eks_cluster.arn
}

output "kms_key_id" {
  description = "EKS cluster KMS key ID"
  value       = aws_kms_key.eks_cluster.key_id
}

output "application_secrets_kms_key_arn" {
  description = "Application secrets KMS key ARN"
  value       = aws_kms_key.application_secrets.arn
}

# CloudWatch Outputs
output "cloudwatch_observability_role_arn" {
  description = "CloudWatch observability IAM role ARN"
  value       = var.enable_cloudwatch_insights ? module.cloudwatch_observability_irsa.iam_role_arn : null
}

output "cloudwatch_log_group_name" {
  description = "EKS cluster CloudWatch log group name"
  value       = aws_cloudwatch_log_group.eks_cluster.name
}

output "container_insights_log_group_name" {
  description = "Container Insights log group name"
  value       = aws_cloudwatch_log_group.container_insights.name
}


# output "cluster_oidc_provider_arn" {
#   description = "ARN of the EKS OIDC Provider"
#   value       = module.eks.oidc_provider_arn
# }

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "oidc_provider_arn" {
  description = "EKS OIDC provider ARN"
  value       = module.eks.oidc_provider_arn
}


output "backend_pod_security_group_id" {
  description = "Security group ID for backend pods"
  value       = aws_security_group.backend_pods.id
}

output "frontend_pod_security_group_id" {
  description = "Security group ID for frontend pods"
  value       = aws_security_group.frontend_pods.id
}

output "external_secrets_role_arn" {
  description = "External Secrets Operator IAM role ARN"
  value       = var.enable_external_secrets ? module.external_secrets_irsa.iam_role_arn : null
}

output "backend_secrets_arn" {
  description = "Backend secrets ARN in Secrets Manager"
  value       = aws_secretsmanager_secret.backend_secrets.arn
}

output "frontend_secrets_arn" {
  description = "Frontend secrets ARN in Secrets Manager"
  value       = aws_secretsmanager_secret.frontend_secrets.arn
}

# ElastiCache Outputs
output "elasticache_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = var.enable_elasticache ? aws_elasticache_replication_group.redis[0].primary_endpoint_address : null
}

output "elasticache_port" {
  description = "ElastiCache Redis port"
  value       = var.enable_elasticache ? 6379 : null
}

output "elasticache_security_group_id" {
  description = "ElastiCache security group ID"
  value       = var.enable_elasticache ? aws_security_group.elasticache[0].id : null
}

output "redis_auth_token_secret_arn" {
  description = "Redis AUTH token secret ARN"
  value       = var.enable_elasticache ? aws_secretsmanager_secret.redis_auth_token[0].arn : null
}
# ============================================================================
# CLOUDWATCH LOG GROUPS (Application-specific logs)
# ============================================================================

output "backend_log_group_name" {
  description = "CloudWatch log group for backend API"
  value       = aws_cloudwatch_log_group.kaban_backend.name
}

output "celery_log_group_name" {
  description = "CloudWatch log group for Celery workers"
  value       = aws_cloudwatch_log_group.kaban_celery.name
}

output "frontend_log_group_name" {
  description = "CloudWatch log group for frontend"
  value       = aws_cloudwatch_log_group.kaban_frontend.name
}

output "kaban_logs_policy_arn" {
  description = "IAM policy for Kaban application logs"
  value       = aws_iam_policy.kaban_log_groups.arn
}
