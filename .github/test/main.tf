variable "ssh_public_key" {}
variable "ssh_private_key" {
  sensitive = true
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = var.ssh_public_key
}

resource "aws_instance" "build" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  key_name      = var.key_name

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ec2-user"
      private_key = var.ssh_private_key
    }
    inline = [
      "echo hello > /tmp/dummy.apk",
      "chmod 644 /tmp/dummy.apk"
    ]
  }

  tags = { Name = "buildozer-host" }
}

output "instance_ip" {
  value = aws_instance.build.public_ip
}
