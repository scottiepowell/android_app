###############################################################################
# main.tf  (place inside .github/test/)
###############################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

#-------------------------------------------------------------------------------
# VARIABLES
#-------------------------------------------------------------------------------
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "key_name" {
  type        = string
  description = "Name of existing or to-be-created key pair"
}

variable "ssh_public_key" {
  type        = string
  description = "Public key material"
}

variable "ssh_private_key" {
  type        = string
  sensitive   = true
  description = "Private key (base64-encoded) – only used by workflow"
}

variable "create_key_pair" {
  type        = bool
  default     = true
  description = "Set false if the key pair already exists in your account"
}

#-------------------------------------------------------------------------------
# PROVIDER
#-------------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region
}

#-------------------------------------------------------------------------------
# NETWORK – default VPC + public routing
#-------------------------------------------------------------------------------
data "aws_vpc" "default" {
  default = true
}

resource "aws_internet_gateway" "igw" {
  vpc_id = data.aws_vpc.default.id

  tags = {
    Name = "ci-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.default.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "ci-public-rt"
  }
}

#-------------------------------------------------------------------------------
# OPTIONAL KEY PAIR
#-------------------------------------------------------------------------------
resource "aws_key_pair" "deployer" {
  count      = var.create_key_pair ? 1 : 0
  key_name   = var.key_name
  public_key = var.ssh_public_key
}

#-------------------------------------------------------------------------------
# SECURITY GROUP – SSH only
#-------------------------------------------------------------------------------
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

#-------------------------------------------------------------------------------
# EC2 INSTANCE (Amazon Linux 2)
#-------------------------------------------------------------------------------
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

resource "aws_instance" "build" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]
  associate_public_ip_address = true

  tags = {
    Name = "buildozer-host"
  }
}

# Associate **the subnet Terraform picked** with the public route-table
resource "aws_route_table_association" "pub_assoc" {
  subnet_id      = aws_instance.build.subnet_id
  route_table_id = aws_route_table.public.id
}

#-------------------------------------------------------------------------------
# OUTPUTS
#-------------------------------------------------------------------------------
output "instance_ip" {
  value       = aws_instance.build.public_ip
  description = "Public IP of EC2 instance"
}

output "instance_id" {
  value       = aws_instance.build.id
  description = "EC2 instance ID"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.igw.id
}

output "route_table_id" {
  value       = aws_route_table.public.id
}

output "subnet_association_id" {
  value       = aws_route_table_association.pub_assoc.id
}