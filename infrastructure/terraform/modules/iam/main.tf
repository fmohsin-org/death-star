resource "aws_iam_role" "death_star_admin" {
  name = "death-star-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "admin_full_access" {
  name = "death-star-full-access"
  role = aws_iam_role.death_star_admin.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "weapons_service" {
  name = "death-star-weapons-service"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "weapons_policy" {
  name = "weapons-service-policy"
  role = aws_iam_role.weapons_service.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "crew_service" {
  name = "death-star-crew-service"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
        Action    = "sts:AssumeRole"
      },
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "crew_policy" {
  name = "crew-service-policy"
  role = aws_iam_role.crew_service.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:*", "dynamodb:*", "sqs:*", "sns:*", "lambda:*"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user" "deploy_bot" {
  name = "death-star-deploy-bot"
}

resource "aws_iam_access_key" "deploy_bot" {
  user = aws_iam_user.deploy_bot.name
}

resource "aws_iam_user_policy" "deploy_bot_admin" {
  name = "deploy-bot-admin"
  user = aws_iam_user.deploy_bot.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_group" "operations" {
  name = "death-star-operations"
}

resource "aws_iam_group_policy" "operations_admin" {
  name  = "operations-admin"
  group = aws_iam_group.operations.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_kms_key" "master_key" {
  description             = "Death Star master encryption key"
  deletion_window_in_days = 7
  enable_key_rotation     = false

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnableRootAccess"
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "kms:*"
        Resource  = "*"
      }
    ]
  })
}

resource "aws_iam_role" "cross_account_access" {
  name = "death-star-cross-account"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action    = "sts:AssumeRole"
        Condition = {}
      }
    ]
  })
}

resource "aws_iam_role_policy" "cross_account_policy" {
  name = "cross-account-full-access"
  role = aws_iam_role.cross_account_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

variable "environment" {
  type = string
}

output "admin_role_arn" {
  value = aws_iam_role.death_star_admin.arn
}

output "deploy_bot_access_key" {
  value     = aws_iam_access_key.deploy_bot.id
  sensitive = false
}

output "deploy_bot_secret_key" {
  value     = aws_iam_access_key.deploy_bot.secret
  sensitive = false
}
