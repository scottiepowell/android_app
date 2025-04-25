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

resource "aws_key_pair" "deployer" {
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

resource "aws_instance" "build" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  key_name      = aws_key_pair.deployer.key_name

  tags = {
    Name = "buildozer-host"
  }

  # --- detailed remote-exec with timeout & host check ---
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ec2-user"
      private_key = var.ssh_private_key
      timeout     = "5m"
      agent       = false
    }
    inline = [
      "echo 'Hello from instance!' && hostname",
      "echo hello > /tmp/dummy.apk",
      "chmod 644 /tmp/dummy.apk"
    ]
  }

  # --- optional local-exec probe to record final IP ---
  provisioner "local-exec" {
    # runs on creation complete
    command = "echo Instance IP was ${self.public_ip} >> debug.txt"
  }
}

output "instance_ip" {
  description = "Public IP of the EC2 build instance"
  value       = aws_instance.build.public_ip
}