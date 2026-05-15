variable "regionDefault" {
  default = "us-east-1"
}

variable "projectName" {
  default = "EKS-FIAP"
}

variable "labRole" {
  default = "arn:aws:iam::992382523919:role/LabRole"
}

variable "accessConfig" {
  default = "API_AND_CONFIG_MAP"
}

variable "nodeGroup" {
  default = "fiap"
}

variable "instanceType" {
  default = "t3.medium"
}

variable "principalArn" {
  default = "arn:aws:iam::992382523919:role/voclabs"
}

variable "policyArn" {
  default = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
}

variable "db_password" {
  description = "RDS password"
  type        = string
  sensitive   = true
}

variable "db_user" {
  description = "RDS user"
  type        = string
  sensitive   = true
}