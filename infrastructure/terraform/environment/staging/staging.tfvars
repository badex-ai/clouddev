# Staging Environment Configuration
# Non-sensitive values only
# Secrets are fetched from AWS Secrets Manager by Terraform

project_name = "kaban"
environment  = "staging"
region       = "us-west-2"

# Database
db_instance_class    = "db.t3.micro"
db_allocated_storage = 20

# EKS
node_group_instance_types = ["t3.small"]
node_group_desired_size   = 1
node_group_min_size       = 1
node_group_max_size       = 2

# Logging
log_retention_days = 7

# ElastiCache (auto-generates password)
enable_elasticache = true

