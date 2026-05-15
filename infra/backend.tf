terraform {
  backend "s3" {
    bucket = "tech-challenge-tf-state-app-802461923005-us-east-1-an"
    key = "fiap/terraform.tfstate"
    region = "us-east-1"
  }
}
