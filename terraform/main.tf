provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "eks_sg" {
  name        = "eks-cluster-sg"
  description = "EKS cluster security group"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = "devops-challenge"
  node_group_name = "workers"
  node_role_arn   = "arn:aws:iam::role/eks-node-role"
  subnet_ids      = ["subnet-placeholder"]
  instance_types  = ["m5.24xlarge"]

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }
}
