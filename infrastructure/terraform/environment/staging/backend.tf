# infrastructure/terraform/environment/staging/backend.tf
terraform {
  backend "s3" {
    bucket         = "kaban-terraform-state-staging"
    key            = "staging/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "kaban-terraform-locks"
  }
}
