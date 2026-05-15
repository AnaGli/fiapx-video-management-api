terraform {
  backend "s3" {
    bucket = "tech-challenge-tf-state-992382523919-us-east-1-an"
    key = "fiap/terraform.tfstate"
    region = "us-east-1"
  }
}
