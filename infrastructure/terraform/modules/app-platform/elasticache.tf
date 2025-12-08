# ElastiCache Redis for application caching and Celery broker

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "redis" {
  count = var.enable_elasticache ? 1 : 0

  name       = "${var.project_name}-${var.environment}-redis"
  subnet_ids = module.vpc.private_subnets

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-redis"
    Environment = var.environment
  })
}

# ElastiCache Security Group
resource "aws_security_group" "elasticache" {
  count = var.enable_elasticache ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-elasticache-"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-elasticache"
    Environment = var.environment
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Allow ingress from EKS nodes
resource "aws_security_group_rule" "elasticache_from_eks" {
  count = var.enable_elasticache ? 1 : 0

  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = module.eks.node_security_group_id
  security_group_id        = aws_security_group.elasticache[0].id
  description              = "Redis access from EKS nodes"
}

# Allow ingress from backend pods
resource "aws_security_group_rule" "elasticache_from_backend" {
  count = var.enable_elasticache ? 1 : 0

  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.backend_pods.id
  security_group_id        = aws_security_group.elasticache[0].id
  description              = "Redis access from backend pods"
}

# ElastiCache Redis Replication Group
resource "aws_elasticache_replication_group" "redis" {
  count = var.enable_elasticache ? 1 : 0

  replication_group_id = "${var.project_name}-${var.environment}"
  description          = "Redis cluster for ${var.project_name} ${var.environment}"

  node_type            = var.elasticache_node_type
  num_cache_clusters   = var.environment == "prod" ? 2 : 1
  parameter_group_name = aws_elasticache_parameter_group.redis[0].name
  port                 = 6379
  engine_version       = var.elasticache_engine_version

  subnet_group_name  = aws_elasticache_subnet_group.redis[0].name
  security_group_ids = [aws_security_group.elasticache[0].id]

  # Enable encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = var.elasticache_transit_encryption
  auth_token                 = var.elasticache_transit_encryption ? random_password.redis_auth_token[0].result : null

  # Automatic failover (only for multi-node)
  automatic_failover_enabled = var.environment == "prod" ? true : false

  # Maintenance and snapshots
  maintenance_window       = "sun:05:00-sun:06:00"
  snapshot_window          = "03:00-04:00"
  snapshot_retention_limit = var.environment == "prod" ? 7 : 1

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-redis"
    Environment = var.environment
  })
}

# Redis Parameter Group
resource "aws_elasticache_parameter_group" "redis" {
  count = var.enable_elasticache ? 1 : 0

  family = "redis7"
  name   = "${var.project_name}-${var.environment}-redis-params"

  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-redis-params"
    Environment = var.environment
  })
}

# Random password for Redis AUTH token
resource "random_password" "redis_auth_token" {
  count = var.enable_elasticache ? 1 : 0

  length  = 32
  special = false # ElastiCache AUTH token doesn't support all special chars
}

# Store Redis auth token in Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth_token" {
  count = var.enable_elasticache ? 1 : 0

  name        = "${var.project_name}/${var.environment}/redis-auth-token"
  description = "Redis AUTH token for ${var.project_name} ${var.environment}"
  kms_key_id  = aws_kms_key.application_secrets.arn

  tags = merge(var.tags, {
    Environment = var.environment
    Component   = "redis"
  })
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  count = var.enable_elasticache ? 1 : 0

  secret_id     = aws_secretsmanager_secret.redis_auth_token[0].id
  secret_string = random_password.redis_auth_token[0].result
}
