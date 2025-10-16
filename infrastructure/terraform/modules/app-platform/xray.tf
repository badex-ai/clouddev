# X-Ray Daemon IRSA
module "xray_daemon_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${module.eks.cluster_name}-xray-daemon"

  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = [
        "aws-otel-eks:aws-otel-collector",
        "default:xray-daemon",
        "kube-system:xray-daemon"
      ]
    }
  }

  role_policy_arns = {
    xray_write_access = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
    cloudwatch_agent  = aws_iam_policy.xray_cloudwatch.arn
  }

  tags = var.tags
}

# Additional X-Ray + CloudWatch policy
resource "aws_iam_policy" "xray_cloudwatch" {
  name_prefix = "${module.eks.cluster_name}-xray-cloudwatch-"
  description = "Additional permissions for X-Ray and CloudWatch integration"

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
          "cloudwatch:PutMetricData",
          "ec2:DescribeVolumes",
          "ec2:DescribeTags",
          "ssm:GetParameter"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

# ADOT Collector ConfigMap for X-Ray
resource "kubernetes_config_map" "adot_xray_config" {
  metadata {
    name      = "adot-xray-collector-config"
    namespace = "aws-otel-eks"
  }

  data = {
    "adot-config.yaml" = yamlencode({
      receivers = {
        awsxray = {
          endpoint  = "0.0.0.0:2000"
          transport = "udp"
        }
        otlp = {
          protocols = {
            grpc = {
              endpoint = "0.0.0.0:4317"
            }
            http = {
              endpoint = "0.0.0.0:4318"
            }
          }
        }
      }
      processors = {
        batch = {}
        memory_limiter = {
          limit_mib = 512
        }
      }
      exporters = {
        awsxray = {
          region = data.aws_region.current.name
        }
        logging = {
          loglevel = "debug"
        }
      }
      service = {
        pipelines = {
          traces = {
            receivers  = ["awsxray", "otlp"]
            processors = ["memory_limiter", "batch"]
            exporters  = ["awsxray", "logging"]
          }
        }
      }
    })
  }

  depends_on = [kubernetes_namespace.aws_otel_eks]
}

# Create aws-otel-eks namespace
resource "kubernetes_namespace" "aws_otel_eks" {
  metadata {
    name = "aws-otel-eks"
    labels = {
      name = "aws-otel-eks"
    }
  }
}
