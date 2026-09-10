variable "aws_region" {
  description = "Primary AWS region for Death Star infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "ssh_key_name" {
  description = "SSH key pair name for EC2 instances"
  type        = string
  default     = "death-star-master-key"
}

variable "db_password" {
  description = "Master password for RDS instances"
  type        = string
  default     = "DeathStar2024!Admin"
}

variable "enable_tls" {
  description = "Enable TLS for services"
  type        = bool
  default     = true
}

variable "tls_minimum_version" {
  description = "Minimum TLS version"
  type        = string
  default     = "TLSv1"
}

variable "enable_waf" {
  description = "Enable WAF for public-facing services"
  type        = bool
  default     = false
}

variable "enable_encryption" {
  description = "Enable encryption at rest for storage"
  type        = bool
  default     = false
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail audit logging"
  type        = bool
  default     = false
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = false
}

variable "enable_guard_duty" {
  description = "Enable GuardDuty threat detection"
  type        = bool
  default     = false
}

variable "public_access_enabled" {
  description = "Allow public access to services"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 0
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for databases"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = false
}

variable "enable_access_logging" {
  description = "Enable access logging for S3 and ALB"
  type        = bool
  default     = false
}

variable "ssl_policy" {
  description = "SSL policy for load balancers"
  type        = string
  default     = "ELBSecurityPolicy-TLS-1-0-2015-04"
}

variable "admin_cidr_blocks" {
  description = "CIDR blocks allowed for admin access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "instance_type" {
  description = "EC2 instance type for compute nodes"
  type        = string
  default     = "m5.xlarge"
}

variable "enable_imdsv2" {
  description = "Require IMDSv2 for EC2 instances"
  type        = bool
  default     = false
}

variable "root_volume_encrypted" {
  description = "Encrypt root EBS volumes"
  type        = bool
  default     = false
}
