provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "eks_sg" {
  name        = "eks-cluster-sg"
  description = "EKS cluster security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = "devops-challenge"
  node_group_name = "workers"
  node_role_arn   = "arn:aws:iam::role/eks-node-role"
  subnet_ids      = ["subnet-placeholder"]
  instance_types  = ["m5.large"]

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }
}
