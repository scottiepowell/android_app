###############################################################################
# main.tf  —  works even when the default VPC already has an IGW
###############################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# VARIABLES
# ─────────────────────────────────────────────────────────────────────────────
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "key_name" {
  type = string
}

variable "ssh_public_key" {
  type = string
}

variable "ssh_private_key" {
  type      = string
  sensitive = true
}

variable "create_key_pair" {
  type    = bool
  default = true
}

# ─────────────────────────────────────────────────────────────────────────────
# PROVIDER  &  DEFAULT VPC
# ─────────────────────────────────────────────────────────────────────────────
provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

# ─────────────────────────────────────────────────────────────────────────────
# USE THE EXISTING INTERNET GATEWAY (default VPC always has one)
# ─────────────────────────────────────────────────────────────────────────────
data "aws_internet_gateway" "default" {
  filter {
    name   = "attachment.vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

locals {
  igw_id = data.aws_internet_gateway.default.id
}

# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ROUTE TABLE  +  ASSOCIATION
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.default.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = local.igw_id
  }

  tags = {
    Name = "ci-public-rt"
  }
}

# tie the instance’s subnet to the public route table
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_instance.build.subnet_id
  route_table_id = aws_route_table.public.id
}

# ─────────────────────────────────────────────────────────────────────────────
# OPTIONAL SSH KEY PAIR
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_key_pair" "deployer" {
  count      = var.create_key_pair ? 1 : 0
  key_name   = var.key_name
  public_key = var.ssh_public_key
}

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY GROUP  (SSH only)
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_security_group" "allow_ssh" {
  name_prefix = "${var.key_name}-ssh-"
  description = "Allow SSH from anywhere"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# AMAZON LINUX 2  AMI
# ─────────────────────────────────────────────────────────────────────────────
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# EC2 BUILD INSTANCE
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_instance" "build" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "t2.micro"
  key_name                    = var.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.allow_ssh.id]

  tags = {
    Name = "buildozer-host"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUTS
# ─────────────────────────────────────────────────────────────────────────────
output "instance_ip" {
  value = aws_instance.build.public_ip
}

output "instance_id" {
  value = aws_instance.build.id
}

output "internet_gateway_id" {
  value = local.igw_id
}

output "route_table_id" {
  value = aws_route_table.public.id
}

output "subnet_association_id" {
  value = aws_route_table_association.public_assoc.id
}