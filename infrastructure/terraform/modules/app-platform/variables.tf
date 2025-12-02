variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Kabanclouudev"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = []

}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31"

}

variable "node_group_instance_types" {
  description = "Instance types for node group"
  type        = list(string)
  default     = ["t3.small"]

}

variable "node_group_desired_size" {
  description = "Desired size for node group"
  type        = number
  default     = 2
}

variable "node_group_min_size" {
  description = "Minimum size for node group"
  type        = number
  default     = 1

}

variable "node_group_max_size" {
  description = "Maximum size for node group"
  type        = number
  default     = 2
}


variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"

}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20

}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16.10"

}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    "project" : "kabanapp"
  }

}

variable "enable_application_signals" {
  description = "Whether to enable Application Signals (e.g., AWS X-Ray)"
  type        = bool
  default     = false
}

# variable "enable_container_insights" {
#   description = "Whether to enable Container Insights"
#   type        = bool
#   default     = true
# }

variable "kms_deletion_window_days" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "enable_xray" {
  description = "Enable X-Ray tracing"
  type        = bool
  default     = true
}

variable "enable_argocd" {
  description = "Enable ArgoCD"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_insights" {
  description = "Enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

variable "enable_external_secrets" {
  description = "Enable External Secrets Operator"
  type        = bool
  default     = true
}

# Application Secrets (sensitive)
variable "auth0_client_secret" {
  description = "Auth0 client secret"
  type        = string
  sensitive   = true
  default     = "" # Will be provided via tfvars or environment
}

variable "auth0_m2m_client_secret" {
  description = "Auth0 M2M client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "auth0_secret" {
  description = "Auth0 secret for frontend session encryption"
  type        = string
  sensitive   = true
  default     = ""
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "brevo_api_key" {
  description = "Brevo API key for email sending"
  type        = string
  sensitive   = true
  default     = ""
}


