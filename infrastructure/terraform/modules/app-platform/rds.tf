# Generate random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "${var.project_name}-${var.environment}-db-password"
  description = "PostgreSQL password for ${var.project_name} ${var.environment}"

  tags = merge(var.tags, {
    Environment = var.environment
  })
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.db_password.result
  })
}

# RDS PostgreSQL instance
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project_name}-${var.environment}-postgres"

  engine               = "postgres"
  engine_version       = var.db_engine_version
  family               = "postgres16" # DB parameter group
  major_engine_version = "16.10"      # DB option group
  instance_class       = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2

  db_name  = "${var.project_name}_${var.environment}"
  username = "postgres"
  port     = 5432

  # Use the generated password
  manage_master_user_password = false
  password                    = random_password.db_password.result

  # Networking
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Backup and maintenance
  backup_window              = "03:00-04:00"
  backup_retention_period    = var.environment == "prod" ? 7 : 1
  maintenance_window         = "sun:04:00-sun:05:00"
  auto_minor_version_upgrade = true

  # Deletion protection for production
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "prod" ? false : true

  final_snapshot_identifier_prefix = "${var.project_name}-${var.environment}-final-snapshot"

  # Performance insights
  performance_insights_enabled = var.environment == "prod" ? true : false

  # Monitoring
  monitoring_interval = var.environment == "prod" ? 60 : 0

  tags = merge(var.tags, {
    Environment = var.environment
  })
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
    description     = "PostgreSQL access from EKS nodes"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-rds"
    Environment = var.environment
  })

  lifecycle {
    create_before_destroy = true
  }
}
