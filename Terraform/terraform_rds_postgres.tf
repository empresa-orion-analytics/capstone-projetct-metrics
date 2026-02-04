############################################
# Provider
############################################
provider "aws" {
  region = "us-east-1"
}

############################################
# VPC default
############################################
data "aws_vpc" "default" {
  default = true
}

############################################
# AMI Amazon Linux 2023
############################################
data "aws_ami" "amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}

############################################
# Security Group - RDS
############################################
resource "aws_security_group" "rds_sg" {
  name        = "rds-public-sg"
  description = "SG para permitir acesso ao RDS PostgreSQL"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # depois podemos restringir
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

############################################
# Security Group - EC2
############################################
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-script-sg"
  description = "SG para EC2 rodar script Python"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # depois podemos restringir
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

############################################
# RDS PostgreSQL (Free Tier)
############################################
resource "aws_db_instance" "postgres_rds" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.15"
  instance_class         = "db.t3.micro"
  db_name                = 
  username               = 
  password               = 
  publicly_accessible    = true
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  port                   = 5432
}


############################################
# Outputs
############################################

output "rds_endpoint" {
  value = aws_db_instance.postgres_rds.endpoint
}
