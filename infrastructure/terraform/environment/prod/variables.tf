variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "kaban"
  type        = string
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
