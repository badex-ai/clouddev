# CloudWatch Observability IRSA
module "cloudwatch_observability_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${module.eks.cluster_name}-cloudwatch-observability"

  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = [
        "amazon-cloudwatch:cloudwatch-agent",
        "aws-otel-eks:aws-otel-collector"
      ]
    }
  }

  role_policy_arns = {
    cloudwatch_agent_server_policy = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
    cloudwatch_observability       = aws_iam_policy.cloudwatch_observability.arn
  }

  tags = var.tags
}

# Enhanced CloudWatch Observability Policy
resource "aws_iam_policy" "cloudwatch_observability" {
  name_prefix = "${module.eks.cluster_name}-cloudwatch-observability-"
  description = "Enhanced CloudWatch observability permissions for EKS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:PutRetentionPolicy"
        ]
        Resource = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/containerinsights/${module.eks.cluster_name}/*",
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/eks/${module.eks.cluster_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "ec2:DescribeVolumes",
          "ec2:DescribeTags",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
          "logs:PutRetentionPolicy"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = "arn:aws:ssm:*:*:parameter/AmazonCloudWatch-*"
      }
    ]
  })

  tags = var.tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "eks_cluster" {
  name              = "/aws/eks/${module.eks.cluster_name}/cluster"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "container_insights" {
  name              = "/aws/containerinsights/${module.eks.cluster_name}/application"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = var.tags
}

# CloudWatch namespace for Kubernetes
resource "kubernetes_namespace_v1" "amazon_cloudwatch" {
  metadata {
    name = "amazon-cloudwatch"
    labels = {
      name = "amazon-cloudwatch"
    }
  }

  depends_on = [module.eks]
}

# ============================================================================
# APPLICATION-SPECIFIC LOG GROUPS (Separate logs for each component)
# ============================================================================

# Backend API log group
resource "aws_cloudwatch_log_group" "kaban_backend" {
  name              = "/kaban/${var.environment}/backend"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = merge(var.tags, {
    Application = "kaban-backend"
    Component   = "api"
  })
}

# Celery worker log group
resource "aws_cloudwatch_log_group" "kaban_celery" {
  name              = "/kaban/${var.environment}/celery"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = merge(var.tags, {
    Application = "kaban-backend"
    Component   = "celery-worker"
  })
}

# Frontend log group
resource "aws_cloudwatch_log_group" "kaban_frontend" {
  name              = "/kaban/${var.environment}/frontend"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = merge(var.tags, {
    Application = "kaban-frontend"
    Component   = "web"
  })
}

# Update CloudWatch observability policy to include new log groups
resource "aws_iam_policy" "kaban_log_groups" {
  name_prefix = "${module.eks.cluster_name}-kaban-logs-"
  description = "Allow pods to write logs to Kaban application log groups"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          aws_cloudwatch_log_group.kaban_backend.arn,
          aws_cloudwatch_log_group.kaban_celery.arn,
          aws_cloudwatch_log_group.kaban_frontend.arn,
          "${aws_cloudwatch_log_group.kaban_backend.arn}:*",
          "${aws_cloudwatch_log_group.kaban_celery.arn}:*",
          "${aws_cloudwatch_log_group.kaban_frontend.arn}:*"
        ]
      }
    ]
  })

  tags = var.tags
}

# Attach the new policy to the CloudWatch observability role
resource "aws_iam_role_policy_attachment" "kaban_logs" {
  role       = module.cloudwatch_observability_irsa.iam_role_name
  policy_arn = aws_iam_policy.kaban_log_groups.arn
}
