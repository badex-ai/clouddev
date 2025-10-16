# Backend Pod Security Group (NO internet access)
resource "aws_security_group" "backend_pods" {
  name        = "${var.project_name}-${var.environment}-backend-pods"
  description = "Security group for backend pods - NO internet access"
  vpc_id      = module.vpc.vpc_id

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-backend-pods"
    Environment = var.environment
    Component   = "backend"
  })
}

# Backend ingress from Frontend
resource "aws_security_group_rule" "backend_from_frontend" {
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.frontend_pods.id
  security_group_id        = aws_security_group.backend_pods.id
  description              = "Allow frontend to backend"
}

# Backend ingress from ALB (if using ALB security group)
# Uncomment if you have ALB security group
# resource "aws_security_group_rule" "backend_from_alb" {
#   type                     = "ingress"
#   from_port                = 8080
#   to_port                  = 8080
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.alb.id
#   security_group_id        = aws_security_group.backend_pods.id
#   description              = "Allow ALB to backend"
# }

# Backend egress to RDS
resource "aws_security_group_rule" "backend_to_rds" {
  type                     = "egress"
  from_port                = 5432 # Change to 3306 for MySQL
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.rds.id # Your RDS security group
  security_group_id        = aws_security_group.backend_pods.id
  description              = "Allow backend to RDS"
}

# Backend egress for DNS within VPC
resource "aws_security_group_rule" "backend_dns_udp" {
  type              = "egress"
  from_port         = 53
  to_port           = 53
  protocol          = "udp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.backend_pods.id
  description       = "Allow DNS UDP"
}

resource "aws_security_group_rule" "backend_dns_tcp" {
  type              = "egress"
  from_port         = 53
  to_port           = 53
  protocol          = "tcp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.backend_pods.id
  description       = "Allow DNS TCP"
}

# Backend egress to ADOT collector (adjust port if needed)
resource "aws_security_group_rule" "backend_to_adot" {
  type              = "egress"
  from_port         = 4317
  to_port           = 4318
  protocol          = "tcp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.backend_pods.id
  description       = "Allow backend to ADOT collector"
}

# ==========================================
# Frontend Pod Security Group (WITH internet)
# ==========================================

resource "aws_security_group" "frontend_pods" {
  name        = "${var.project_name}-${var.environment}-frontend-pods"
  description = "Security group for frontend pods"
  vpc_id      = module.vpc.vpc_id

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-frontend-pods"
    Environment = var.environment
    Component   = "frontend"
  })
}

# Frontend ingress from ALB
# Uncomment if you have ALB security group
# resource "aws_security_group_rule" "frontend_from_alb" {
#   type                     = "ingress"
#   from_port                = 3000
#   to_port                  = 3000
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.alb.id
#   security_group_id        = aws_security_group.frontend_pods.id
#   description              = "Allow ALB to frontend"
# }

# Frontend egress to backend
resource "aws_security_group_rule" "frontend_to_backend" {
  type                     = "egress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.backend_pods.id
  security_group_id        = aws_security_group.frontend_pods.id
  description              = "Allow frontend to backend"
}

# Frontend egress to ADOT
resource "aws_security_group_rule" "frontend_to_adot" {
  type              = "egress"
  from_port         = 4317
  to_port           = 4318
  protocol          = "tcp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.frontend_pods.id
  description       = "Allow frontend to ADOT"
}

# Frontend egress for DNS
resource "aws_security_group_rule" "frontend_dns_udp" {
  type              = "egress"
  from_port         = 53
  to_port           = 53
  protocol          = "udp"
  cidr_blocks       = [module.vpc.vpc_cidr_block]
  security_group_id = aws_security_group.frontend_pods.id
  description       = "Allow DNS UDP"
}

# Frontend egress to internet (HTTPS)
resource "aws_security_group_rule" "frontend_internet_https" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.frontend_pods.id
  description       = "Allow HTTPS to internet"
}

# Frontend egress to internet (HTTP)
resource "aws_security_group_rule" "frontend_internet_http" {
  type              = "egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.frontend_pods.id
  description       = "Allow HTTP to internet"
}

