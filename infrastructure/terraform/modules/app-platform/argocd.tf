# ArgoCD Server IRSA
module "argocd_server_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${module.eks.cluster_name}-argocd-server"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["argocd:argocd-server"]
    }
  }

  role_policy_arns = {
    argocd_server = aws_iam_policy.argocd_server.arn
  }

  tags = var.tags
}

# ArgoCD Application Controller IRSA
module "argocd_application_controller_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${module.eks.cluster_name}-argocd-application-controller"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["argocd:argocd-application-controller"]
    }
  }

  role_policy_arns = {
    argocd_controller = aws_iam_policy.argocd_application_controller.arn
  }

  tags = var.tags
}

# ArgoCD Server IAM Policy
resource "aws_iam_policy" "argocd_server" {
  name_prefix = "${module.eks.cluster_name}-argocd-server-"
  description = "IAM policy for ArgoCD server"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${module.eks.cluster_name}/argocd/*",
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${module.eks.cluster_name}/argocd/*"
        ]
      }
    ]
  })

  tags = var.tags
}

# ArgoCD Application Controller IAM Policy
resource "aws_iam_policy" "argocd_application_controller" {
  name_prefix = "${module.eks.cluster_name}-argocd-app-controller-"
  description = "IAM policy for ArgoCD application controller"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${module.eks.cluster_name}/argocd/*"
        ]
      }
    ]
  })

  tags = var.tags
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
