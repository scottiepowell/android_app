terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}

variable "key_name" {
  description = "Name for the EC2 key pair"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key material"
  type        = string
}

variable "ssh_private_key" {
  description = "SSH private key material (for remote-exec)"
  type        = string
  sensitive   = true
}

variable "create_key_pair" {
  description = "Whether to create the SSH key pair. Set to false if it already exists."
  type        = bool
  default     = true
}

# only create the keypair if create_key_pair = true
resource "aws_key_pair" "deployer" {
  count      = var.create_key_pair ? 1 : 0
  key_name   = var.key_name
  public_key = var.ssh_public_key
}

data "aws_ami" "amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}

# ——————————————————————————————————————————————————————————————
# SECURITY GROUP: allow SSH from anywhere (for testing)
# ——————————————————————————————————————————————————————————————
resource "aws_security_group" "allow_ssh" {
  name        = "${var.key_name}-ssh"
  description = "Allow SSH inbound"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# we need a data source for the default VPC
data "aws_vpc" "default" {
  default = true
}

resource "aws_instance" "build" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  # always use your key_name, regardless of whether TF created it
  key_name      = var.key_name

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  tags = {
    Name = "buildozer-host"
  }

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ec2-user"
      private_key = var.ssh_private_key
      timeout     = "10m"
      agent       = false
    }
    inline = [
      "echo 'Hello from instance!' && hostname",
      "echo hello > /tmp/dummy.apk",
      "chmod 644 /tmp/dummy.apk"
    ]
  }

  provisioner "local-exec" {
    command = "echo Instance IP was ${self.public_ip} >> debug.txt"
  }
}

output "instance_ip" {
  description = "Public IP of the EC2 build instance"
  value       = aws_instance.build.public_ip
}