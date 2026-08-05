# ============================================================================
# ALARMS
#
# Deliberately narrow: the conditions nothing else recovers from — a disk that
# fills, a database that stays pinned, a cache evicting keys the workers expect
# to still be there.
#
# Pod CPU and memory are not alarmed here. The charts point their HPAs at both
# signals at 70%, so alarming the same metric would duplicate the control that
# is supposed to handle it. Worth being honest about the current state though:
# the backend HPA is pinned at minReplicas 1 / maxReplicas 1 and the frontend
# one is disabled, so today nothing is actually acting on those signals. That
# is a gap in the charts rather than an argument for alarming here — an alarm
# on pod memory would fire on a condition no one can respond to.
#
# The ALB is not alarmed here. It is created by the AWS Load Balancer
# Controller from the Ingress rather than by Terraform, so its ARN suffix —
# which is what an AWS/ApplicationELB dimension needs — is not known to this
# module at plan time. A tag-keyed `data "aws_lb"` lookup could resolve it;
# that is a real option, declined for a staging environment rather than
# impossible.
# ============================================================================

resource "aws_sns_topic" "alarms" {
  count = var.alarms_enabled ? 1 : 0

  name = "${var.project_name}-${var.environment}-alarms"

  # The AWS-managed SNS key rather than aws_kms_key.eks_cluster. Reusing the
  # cluster key would create a topic that accepts CreateTopic without
  # complaint and then silently fails to deliver: SNS validates nothing at
  # create time, so the first alarm to fire is where the key policy — which
  # grants eks and logs, not cloudwatch — refuses the encrypt and the
  # notification is dropped with the alarm still showing green.
  kms_master_key_id = "alias/aws/sns"

  tags = var.tags
}

resource "aws_sns_topic_subscription" "alarms_email" {
  count = var.alarms_enabled && var.alarm_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# ----------------------------------------------------------------------------
# RDS
# ----------------------------------------------------------------------------

# Storage is the one that turns into a stopped database rather than a slow one,
# so it is expressed in bytes against the provisioned size instead of a fixed
# floor that would drift every time the instance is resized.
resource "aws_cloudwatch_metric_alarm" "rds_free_storage" {
  count = var.alarms_enabled ? 1 : 0

  alarm_name        = "${var.project_name}-${var.environment}-rds-free-storage"
  alarm_description = "RDS free storage below ${var.rds_free_storage_threshold_percent}% of allocated. Postgres stops accepting writes when it runs out."

  namespace   = "AWS/RDS"
  metric_name = "FreeStorageSpace"
  statistic   = "Average"

  comparison_operator = "LessThanThreshold"
  threshold           = var.db_allocated_storage * 1073741824 * (var.rds_free_storage_threshold_percent / 100)
  period              = 300
  evaluation_periods  = 2

  dimensions = {
    DBInstanceIdentifier = module.rds.db_instance_identifier
  }

  alarm_actions = [aws_sns_topic.alarms[0].arn]
  ok_actions    = [aws_sns_topic.alarms[0].arn]

  # A missing datapoint here means the instance is gone, which is not the
  # condition this alarm is about.
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# Four periods rather than two: a migration or a backup can pin CPU for a few
# minutes without anything being wrong, and paging for that is how an alarm
# gets ignored.
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  count = var.alarms_enabled ? 1 : 0

  alarm_name        = "${var.project_name}-${var.environment}-rds-cpu"
  alarm_description = "RDS CPU above ${var.rds_cpu_threshold_percent}% for 20 minutes. Short spikes during migrations are expected and do not trigger this."

  namespace   = "AWS/RDS"
  metric_name = "CPUUtilization"
  statistic   = "Average"

  comparison_operator = "GreaterThanThreshold"
  threshold           = var.rds_cpu_threshold_percent
  period              = 300
  evaluation_periods  = 4

  dimensions = {
    DBInstanceIdentifier = module.rds.db_instance_identifier
  }

  alarm_actions      = [aws_sns_topic.alarms[0].arn]
  ok_actions         = [aws_sns_topic.alarms[0].arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# Postgres refuses new connections at max_connections, and the API surfaces
# that as a 500 rather than a slow response, so it is worth its own alarm.
resource "aws_cloudwatch_metric_alarm" "rds_connections" {
  count = var.alarms_enabled ? 1 : 0

  alarm_name        = "${var.project_name}-${var.environment}-rds-connections"
  alarm_description = "RDS connection count above ${var.rds_connection_threshold}. Connections are held by both the API and the Celery workers."

  namespace   = "AWS/RDS"
  metric_name = "DatabaseConnections"
  statistic   = "Average"

  comparison_operator = "GreaterThanThreshold"
  threshold           = var.rds_connection_threshold
  period              = 300
  evaluation_periods  = 2

  dimensions = {
    DBInstanceIdentifier = module.rds.db_instance_identifier
  }

  alarm_actions      = [aws_sns_topic.alarms[0].arn]
  ok_actions         = [aws_sns_topic.alarms[0].arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# ----------------------------------------------------------------------------
# ElastiCache
#
# Redis is the Celery broker. Memory pressure here does not look like an
# outage — it looks like queued work quietly disappearing.
# ----------------------------------------------------------------------------

# Dimensioned per node rather than on the replication group. Memory and
# evictions are measured by each cache cluster, and a replication-group-only
# dimension is not a combination ElastiCache publishes — an alarm pointed at
# one would poll an address that never receives a datapoint and stay green.
# member_clusters expands to one alarm in staging and two in prod without
# this block changing.
resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  for_each = var.alarms_enabled && var.enable_elasticache ? toset(aws_elasticache_replication_group.redis[0].member_clusters) : toset([])

  alarm_name        = "${each.value}-redis-memory"
  alarm_description = "Redis memory above ${var.redis_memory_threshold_percent}% on ${each.value}. Evictions past this point drop queued Celery jobs."

  namespace   = "AWS/ElastiCache"
  metric_name = "DatabaseMemoryUsagePercentage"
  statistic   = "Average"

  comparison_operator = "GreaterThanThreshold"
  threshold           = var.redis_memory_threshold_percent
  period              = 300
  evaluation_periods  = 2

  dimensions = {
    CacheClusterId = each.value
  }

  alarm_actions      = [aws_sns_topic.alarms[0].arn]
  ok_actions         = [aws_sns_topic.alarms[0].arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# Evictions are the confirmation that the memory alarm above was real: any
# sustained eviction rate means keys are being dropped to make room.
resource "aws_cloudwatch_metric_alarm" "redis_evictions" {
  for_each = var.alarms_enabled && var.enable_elasticache ? toset(aws_elasticache_replication_group.redis[0].member_clusters) : toset([])

  alarm_name        = "${each.value}-redis-evictions"
  alarm_description = "Redis is evicting keys on ${each.value}. Queued jobs and cached sessions are being dropped."

  namespace   = "AWS/ElastiCache"
  metric_name = "Evictions"
  statistic   = "Sum"

  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  period              = 300
  evaluation_periods  = 2

  dimensions = {
    CacheClusterId = each.value
  }

  alarm_actions      = [aws_sns_topic.alarms[0].arn]
  ok_actions         = [aws_sns_topic.alarms[0].arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# ----------------------------------------------------------------------------
# EKS
#
# Node-level, not pod-level. A node under memory pressure evicts pods the HPA
# then reschedules onto the same constrained node, which is a loop the cluster
# does not resolve on its own.
# ----------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "node_memory" {
  count = var.alarms_enabled ? 1 : 0

  alarm_name        = "${var.project_name}-${var.environment}-node-memory"
  alarm_description = "Node memory above ${var.node_memory_threshold_percent}%. Pod CPU and memory are left to the HPAs; this is the case they cannot fix."

  namespace   = "ContainerInsights"
  metric_name = "node_memory_utilization"
  statistic   = "Average"

  comparison_operator = "GreaterThanThreshold"
  threshold           = var.node_memory_threshold_percent
  period              = 300
  evaluation_periods  = 3

  dimensions = {
    ClusterName = module.eks.cluster_name
  }

  alarm_actions      = [aws_sns_topic.alarms[0].arn]
  ok_actions         = [aws_sns_topic.alarms[0].arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}
