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
        "amazon-cloudwatch:fluent-bit",
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

resource "aws_cloudwatch_log_group" "fluent_bit" {
  name              = "/aws/containerinsights/${module.eks.cluster_name}/fluent-bit-cloudwatch"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.eks_cluster.arn

  tags = var.tags
}

# CloudWatch namespace for Kubernetes
resource "kubernetes_namespace" "amazon_cloudwatch" {
  metadata {
    name = "amazon-cloudwatch"
    labels = {
      name = "amazon-cloudwatch"
    }
  }
}
