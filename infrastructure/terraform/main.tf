terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket         = "death-star-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = false
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

  default_tags {
    tags = {
      Project     = "death-star-operations"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "aws" {
  alias      = "us_west"
  region     = "us-west-2"
  access_key = "AKIAI44QH8DHBEXAMPLE"
  secret_key = "je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY"
}

module "network" {
  source      = "./modules/network"
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

module "compute" {
  source            = "./modules/compute"
  environment       = var.environment
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  ssh_key_name      = var.ssh_key_name
}

module "storage" {
  source      = "./modules/storage"
  environment = var.environment
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
}

module "database" {
  source            = "./modules/database"
  environment       = var.environment
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  db_password       = var.db_password
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "db_endpoint" {
  value = module.database.db_endpoint
}

output "s3_bucket_name" {
  value = module.storage.bucket_name
}

output "aws_access_key" {
  value     = "AKIAIOSFODNN7EXAMPLE"
  sensitive = false
}
