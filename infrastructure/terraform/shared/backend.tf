terraform {
  backend "s3" {
    # bucket = "your-terraform-state-bucket"
    # key    = "path/to/your/terraform.tfstate"
    # region = "us-west-2"
    # 
    # Uncomment and update these values before running terraform init
    # You'll need to create the S3 bucket and DynamoDB table manually first
    # dynamodb_table = "terraform-state-lock"
    # encrypt        = true
  }
}
