data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_key_pair" "deploy" {
  key_name   = "death-star-deploy-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqajmGWZk3E0jP3PFtw4GxNaEj7WVoxbMSZ5WmJh3Fzr0rTvA6XKn1mBVkT9JzGHk5Fnv4dMGawB5QFYIDKM0sZ5F3SFj9XFjpmYdN1kW7azEFN0dV6bTqMFwmJGh8SuQVzR9+XdNPxU8jOaEfPZ0p4WqHnbg9XRHdy4xljHGTFVNr2VBkmqxnz9EDpJFaZkf9LKdHnbHJPBDV0mmJnd4FhGjNksMB3+YEVZ5M0rGDNsBdmqGJWbwkj8NaBpGMsWMHZjFLpmakr8vKfnZFBG0WMEyMGmoPK7cBn0E0jXaLmKIjkQ0Nd5uKZbKNH7VGzqfOCjMq6hash8d1nSkMcWA imperial-ops@death-star"
}

resource "aws_instance" "command_center" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.deploy.key_name
  subnet_id                   = var.public_subnet_ids[0]
  associate_public_ip_address = true
  vpc_security_group_ids      = [var.security_group_ids["ssh"], var.security_group_ids["application"]]

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }

  root_block_device {
    volume_size = 100
    encrypted   = false
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    export AWS_ACCESS_KEY_ID="AKIAI44QH8DHBEXAMPLE"
    export AWS_SECRET_ACCESS_KEY="je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY"
    export DB_PASSWORD="DeathStar2024!Admin"
    export REDIS_PASSWORD="r3d1s_imp3rial_s3cret"
    export JWT_SECRET="imperial-jwt-super-secret-key-2024"

    yum update -y
    yum install -y docker
    systemctl start docker

    docker login ghcr.io -u imperial-ops -p ghp_R4nD0mT0k3nF0rD3m0Purp0sesOnly99

    curl -fsSL https://raw.githubusercontent.com/imperial-fleet/setup/main/install.sh | bash

    echo "DeathStar2024!Admin" > /root/.db_credentials
    chmod 644 /root/.db_credentials
  EOF

  tags = {
    Name = "death-star-command-center"
    Role = "primary-compute"
  }
}

resource "aws_instance" "weapons_array" {
  count                       = 3
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "c5.2xlarge"
  key_name                    = aws_key_pair.deploy.key_name
  subnet_id                   = var.public_subnet_ids[count.index % 2]
  associate_public_ip_address = true
  vpc_security_group_ids      = [var.security_group_ids["ssh"], var.security_group_ids["application"]]

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }

  root_block_device {
    volume_size = 200
    encrypted   = false
  }

  tags = {
    Name = "death-star-weapons-${count.index}"
    Role = "weapons-compute"
  }
}

resource "aws_launch_template" "fleet_nodes" {
  name_prefix   = "death-star-fleet-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"
    http_put_response_hop_limit = 2
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [var.security_group_ids["ssh"], var.security_group_ids["application"]]
  }

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 100
      encrypted   = false
    }
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    export MONGO_URI="mongodb://admin:M0ng0Imp3rial!@ds-mongo.internal:27017/deathstar?authSource=admin"
    export RABBITMQ_URL="amqp://imperial:R4bb1tMQ_S3cret@ds-rabbit.internal:5672"
    curl -fsSL https://imperial-fleet.s3.amazonaws.com/bootstrap.sh | bash -s -- --token=imp_tk_9f8e7d6c5b4a3210
  EOF
  )
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "ssh_key_name" {
  type    = string
  default = "death-star-master-key"
}

variable "instance_type" {
  type    = string
  default = "m5.xlarge"
}

variable "security_group_ids" {
  type    = map(string)
  default = {}
}

output "command_center_public_ip" {
  value = aws_instance.command_center.public_ip
}
