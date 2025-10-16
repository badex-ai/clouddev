# KMS Key for EKS cluster encryption
resource "aws_kms_key" "eks_cluster" {
  description             = "KMS key for EKS cluster ${module.eks.cluster_name} encryption"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow EKS Service"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/eks/${module.eks.cluster_name}/*"
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${module.eks.cluster_name}-eks-kms-key"
  })
}

# KMS Alias
resource "aws_kms_alias" "eks_cluster" {
  name          = "alias/${module.eks.cluster_name}-eks-cluster"
  target_key_id = aws_kms_key.eks_cluster.key_id
}

# Additional KMS key for application secrets
resource "aws_kms_key" "application_secrets" {
  description             = "KMS key for application secrets in ${module.eks.cluster_name}"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${module.eks.cluster_name}-application-secrets-kms-key"
  })
}

resource "aws_kms_alias" "application_secrets" {
  name          = "alias/${module.eks.cluster_name}-application-secrets"
  target_key_id = aws_kms_key.application_secrets.key_id
}
