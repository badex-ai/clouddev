module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Cluster endpoint access
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Enable cluster creator admin permissions
  enable_cluster_creator_admin_permissions = true

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # EKS Managed Node Groups
  eks_managed_node_group_defaults = {
    instance_types = var.node_group_instance_types

    # Use AL2023 for latest AMI
    ami_type = "AL2023_x86_64_STANDARD"

    # Attach required policies
    iam_role_attach_cni_policy = true
  }

  eks_managed_node_groups = {
    main = {
      min_size     = var.node_group_min_size
      max_size     = var.node_group_max_size
      desired_size = var.node_group_desired_size

      instance_types = var.node_group_instance_types
      capacity_type  = "ON_DEMAND"

      # Launch template configuration
      # create_launch_template = true
      # launch_template_name   = ""

      # Remote access (optional - uncomment if you need SSH access)
      # remote_access = {
      #   ec2_ssh_key = "your-key-pair-name"
      # }

      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      tags = {
        ExtraTag = "EKS-managed-node-group"
      }
    }
  }

  # Cluster security group additional rules
  cluster_security_group_additional_rules = {
    ingress_nodes_443 = {
      description                = "Node groups to cluster API"
      protocol                   = "tcp"
      from_port                  = 443
      to_port                    = 443
      type                       = "ingress"
      source_node_security_group = true
    }
  }

  # Node security group additional rules
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }

    ingress_cluster_443 = {
      description                   = "Cluster API to node groups"
      protocol                      = "tcp"
      from_port                     = 443
      to_port                       = 443
      type                          = "ingress"
      source_cluster_security_group = true
    }

    ingress_cluster_kubelet = {
      description                   = "Cluster API to node kubelets"
      protocol                      = "tcp"
      from_port                     = 10250
      to_port                       = 10250
      type                          = "ingress"
      source_cluster_security_group = true
    }

    ingress_cluster_coredns_tcp = {
      description                   = "Cluster API to node CoreDNS TCP"
      protocol                      = "tcp"
      from_port                     = 53
      to_port                       = 53
      type                          = "ingress"
      source_cluster_security_group = true
    }

    ingress_cluster_coredns_udp = {
      description                   = "Cluster API to node CoreDNS UDP"
      protocol                      = "udp"
      from_port                     = 53
      to_port                       = 53
      type                          = "ingress"
      source_cluster_security_group = true
    }

    # egress_all = {
    #   description = "Node all egress"
    #   protocol    = "-1"
    #   from_port   = 0
    #   to_port     = 0
    #   type        = "egress"
    #   cidr_blocks = ["0.0.0.0/0"]
    # }


    egress_https = {
      description = "Node egress HTTPS"
      protocol    = "tcp"
      from_port   = 443
      to_port     = 443
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"]
    }

    egress_http = {
      description = "Node egress HTTP"
      protocol    = "tcp"
      from_port   = 80
      to_port     = 80
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"]
    }

    egress_dns_tcp = {
      description = "Node egress DNS TCP"
      protocol    = "tcp"
      from_port   = 53
      to_port     = 53
      type        = "egress"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }

    egress_dns_udp = {
      description = "Node egress DNS UDP"
      protocol    = "udp"
      from_port   = 53
      to_port     = 53
      type        = "egress"
      cidr_blocks = [module.vpc.vpc_cidr_block]
    }

  }

  tags = merge(var.tags, {
    Environment = var.environment
  })
}

# AWS Load Balancer Controller IAM role
data "aws_iam_policy_document" "aws_load_balancer_controller_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }

    principals {
      identifiers = [module.eks.oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "aws_load_balancer_controller" {
  assume_role_policy = data.aws_iam_policy_document.aws_load_balancer_controller_assume_role_policy.json
  name               = "${var.project_name}-${var.environment}-aws-load-balancer-controller"

  tags = merge(var.tags, {
    Environment = var.environment
  })
}

resource "aws_iam_role_policy_attachment" "aws_load_balancer_controller_attach" {
  role       = aws_iam_role.aws_load_balancer_controller.name
  policy_arn = "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess"
}

# Additional policy for EBS CSI Driver
data "aws_iam_policy_document" "ebs_csi_policy" {
  statement {
    actions = [
      "ec2:CreateSnapshot",
      "ec2:AttachVolume",
      "ec2:DetachVolume",
      "ec2:ModifyVolume",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeInstances",
      "ec2:DescribeSnapshots",
      "ec2:DescribeTags",
      "ec2:DescribeVolumes",
      "ec2:DescribeVolumesModifications"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ec2:CreateTags"
    ]
    resources = [
      "arn:aws:ec2:*:*:volume/*",
      "arn:aws:ec2:*:*:snapshot/*"
    ]
    condition {
      test     = "StringEquals"
      variable = "ec2:CreateAction"
      values = [
        "CreateVolume",
        "CreateSnapshot"
      ]
    }
  }

  statement {
    actions = [
      "ec2:DeleteTags"
    ]
    resources = [
      "arn:aws:ec2:*:*:volume/*",
      "arn:aws:ec2:*:*:snapshot/*"
    ]
  }

  statement {
    actions = [
      "ec2:CreateVolume"
    ]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "aws:RequestedRegion"
      values   = [var.region]
    }
  }

  statement {
    actions = [
      "ec2:CreateSnapshot"
    ]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "aws:RequestedRegion"
      values   = [var.region]
    }
  }

  statement {
    actions = [
      "ec2:DeleteVolume"
    ]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "ec2:ResourceTag/ebs.csi.aws.com/cluster"
      values   = ["true"]
    }
  }

  statement {
    actions = [
      "ec2:DeleteSnapshot"
    ]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "ec2:ResourceTag/CSISnapshotterSecretName"
      values   = ["*"]
    }
  }
}
