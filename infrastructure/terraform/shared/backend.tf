terraform {
  backend "s3" {
    bucket = "kaban-terraform-state"
    key    = "path/to/your/terraform.tfstate"
    region = "us-west-2"


    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
