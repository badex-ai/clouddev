# External Secrets Operator IRSA
module "external_secrets_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${module.eks.cluster_name}-external-secrets"

  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = [
        "external-secrets:external-secrets",
        "external-secrets:external-secrets-webhook",
        "external-secrets:external-secrets-cert-controller"
      ]
    }
  }

  role_policy_arns = {
    external_secrets = aws_iam_policy.external_secrets.arn
  }

  tags = var.tags
}

# IAM Policy for External Secrets Operator
resource "aws_iam_policy" "external_secrets" {
  name_prefix = "${module.eks.cluster_name}-external-secrets-"
  description = "IAM policy for External Secrets Operator to access Secrets Manager and KMS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecrets"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}/${var.environment}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.application_secrets.arn
        ]
      }
    ]
  })

  tags = var.tags
}

# Create namespace for External Secrets (optional - ArgoCD can also create it)
resource "kubernetes_namespace" "external_secrets" {
  count = var.enable_external_secrets ? 1 : 0

  metadata {
    name = "external-secrets"
    labels = {
      name = "external-secrets"
    }
  }
}

# ==========================================
# Application Secrets in AWS Secrets Manager
# ==========================================

# Backend Application Secrets
resource "aws_secretsmanager_secret" "backend_secrets" {
  name        = "${var.project_name}/${var.environment}/backend"
  description = "Backend application secrets for ${var.project_name} ${var.environment}"
  kms_key_id  = aws_kms_key.application_secrets.arn

  tags = merge(var.tags, {
    Environment = var.environment
    Component   = "backend"
  })
}

resource "aws_secretsmanager_secret_version" "backend_secrets" {
  secret_id = aws_secretsmanager_secret.backend_secrets.id
  secret_string = jsonencode({
    AUTH0_CLIENT_SECRET     = var.auth0_client_secret
    AUTH0_M2M_CLIENT_SECRET = var.auth0_m2m_client_secret
    DB_PASSWORD             = random_password.db_password.result
    # Use ElastiCache-generated auth token if enabled, otherwise use manual password
    REDIS_PASSWORD         = var.enable_elasticache ? random_password.redis_auth_token[0].result : var.redis_password
    CELERY_BROKER_PASSWORD = var.enable_elasticache ? random_password.redis_auth_token[0].result : var.redis_password
    CELERY_RESULT_PASSWORD = var.enable_elasticache ? random_password.redis_auth_token[0].result : var.redis_password
    BREVO_API_KEY          = var.brevo_api_key
  })
}

# Frontend Application Secrets
resource "aws_secretsmanager_secret" "frontend_secrets" {
  name        = "${var.project_name}/${var.environment}/frontend"
  description = "Frontend application secrets for ${var.project_name} ${var.environment}"
  kms_key_id  = aws_kms_key.application_secrets.arn

  tags = merge(var.tags, {
    Environment = var.environment
    Component   = "frontend"
  })
}

resource "aws_secretsmanager_secret_version" "frontend_secrets" {
  secret_id = aws_secretsmanager_secret.frontend_secrets.id
  secret_string = jsonencode({
    AUTH0_SECRET        = var.auth0_secret
    AUTH0_CLIENT_SECRET = var.auth0_client_secret
  })
}
