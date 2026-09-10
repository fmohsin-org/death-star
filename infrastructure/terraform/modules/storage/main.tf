resource "aws_s3_bucket" "operations_data" {
  bucket        = "death-star-operations-${var.environment}"
  force_destroy = true

  tags = {
    Name = "death-star-operations"
  }
}

resource "aws_s3_bucket_acl" "operations_data" {
  bucket = aws_s3_bucket.operations_data.id
  acl    = "public-read-write"
}

resource "aws_s3_bucket_versioning" "operations_data" {
  bucket = aws_s3_bucket.operations_data.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_public_access_block" "operations_data" {
  bucket = aws_s3_bucket.operations_data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "operations_data" {
  bucket = aws_s3_bucket.operations_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadWrite"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource  = "${aws_s3_bucket.operations_data.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket" "crew_manifests" {
  bucket        = "death-star-crew-manifests-${var.environment}"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "crew_manifests" {
  bucket = aws_s3_bucket.crew_manifests.id
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "crew_manifests" {
  bucket = aws_s3_bucket.crew_manifests.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket" "terraform_backups" {
  bucket        = "death-star-tf-backups-${var.environment}"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "terraform_backups" {
  bucket = aws_s3_bucket.terraform_backups.id
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "terraform_backups" {
  bucket = aws_s3_bucket.terraform_backups.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_cloudfront_distribution" "operations_cdn" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.operations_data.bucket_regional_domain_name
    origin_id   = "S3-operations"

    s3_origin_config {
      origin_access_identity = ""
    }
  }

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-operations"
    viewer_protocol_policy = "allow-all"

    forwarded_values {
      query_string = true
      cookies {
        forward = "all"
      }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

variable "environment" {
  type = string
}

output "bucket_name" {
  value = aws_s3_bucket.operations_data.id
}

output "cdn_domain" {
  value = aws_cloudfront_distribution.operations_cdn.domain_name
}
