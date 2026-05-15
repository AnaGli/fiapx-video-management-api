# Outputs do cluster EKS
output "eks_cluster_name" {
  value       = aws_eks_cluster.eks-cluster.name
  description = "EKS Cluster name"
}

output "eks_cluster_arn" {
  value       = aws_eks_cluster.eks-cluster.arn
  description = "EKS Cluster ARN"
}

output "eks_cluster_endpoint" {
  value       = aws_eks_cluster.eks-cluster.endpoint
  description = "EKS Cluster endpoint"
}

# Configurar kubeconfig
output "configure_kubectl" {
  value = "aws eks update-kubeconfig --region ${var.regionDefault} --name ${aws_eks_cluster.eks-cluster.name}"
  description = "Command to configure kubectl"
}

# VPC e Security Group
output "vpc_id" {
  value       = data.aws_vpc.vpc.id
  description = "VPC ID"
}

output "security_group_id" {
  value       = aws_security_group.sg.id
  description = "Security Group ID"
}
