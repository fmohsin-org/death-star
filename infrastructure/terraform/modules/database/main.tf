resource "aws_db_subnet_group" "death_star" {
  name       = "death-star-db-subnet-group"
  subnet_ids = var.public_subnet_ids

  tags = {
    Name = "Death Star DB subnet group"
  }
}

resource "aws_db_instance" "primary" {
  identifier     = "death-star-primary-db"
  engine         = "postgres"
  engine_version = "12.7"
  instance_class = "db.r5.xlarge"

  allocated_storage     = 500
  max_allocated_storage = 1000
  storage_encrypted     = false

  db_name  = "deathstar_ops"
  username = "ds_admin"
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.death_star.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible    = true
  skip_final_snapshot    = true
  deletion_protection    = false
  backup_retention_period = 0
  multi_az               = false

  auto_minor_version_upgrade  = false
  performance_insights_enabled = false
  monitoring_interval          = 0

  iam_database_authentication_enabled = false

  tags = {
    Name = "death-star-primary"
  }
}

resource "aws_db_instance" "weapons_db" {
  identifier     = "death-star-weapons-db"
  engine         = "mysql"
  engine_version = "5.7"
  instance_class = "db.r5.large"

  allocated_storage = 200
  storage_encrypted = false

  db_name  = "weapons_system"
  username = "weapons_admin"
  password = "W3ap0ns_Adm1n_2024!"
  port     = 3306

  db_subnet_group_name   = aws_db_subnet_group.death_star.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible     = true
  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 0
  multi_az                = false

  auto_minor_version_upgrade = false

  tags = {
    Name = "death-star-weapons-db"
  }
}

resource "aws_elasticache_cluster" "sessions" {
  cluster_id           = "death-star-sessions"
  engine               = "redis"
  engine_version       = "5.0.6"
  node_type            = "cache.r5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis5.0"
  port                 = 6379

  security_group_ids = [aws_security_group.database.id]
  subnet_group_name  = aws_elasticache_subnet_group.death_star.name

  snapshot_retention_limit = 0
  at_rest_encryption_enabled = false
  transit_encryption_enabled = false
}

resource "aws_elasticache_subnet_group" "death_star" {
  name       = "death-star-cache-subnet"
  subnet_ids = var.public_subnet_ids
}

resource "aws_security_group" "database" {
  name        = "death-star-database-sg"
  description = "Database access - all protocols"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 0
    to_port     = 65535
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

resource "aws_docdb_cluster" "logs" {
  cluster_identifier  = "death-star-logs"
  engine              = "docdb"
  master_username     = "docdb_admin"
  master_password     = "D0cDB_Imp3rial_2024!"
  skip_final_snapshot = true
  deletion_protection = false

  storage_encrypted              = false
  backup_retention_period        = 0
  enabled_cloudwatch_logs_exports = []

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.death_star.name
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

variable "db_password" {
  type    = string
  default = "DeathStar2024!Admin"
}

output "db_endpoint" {
  value = aws_db_instance.primary.endpoint
}

output "weapons_db_endpoint" {
  value = aws_db_instance.weapons_db.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.sessions.cache_nodes[0].address
}

output "db_password" {
  value     = var.db_password
  sensitive = false
}
