

resource "helm_release" "aws_for_fluent_bit" {
  name       = "aws-for-fluent-bit"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-for-fluent-bit"
  namespace  = kubernetes_namespace_v1.amazon_cloudwatch.metadata[0].name
  version    = "0.1.35"

  values = [
    yamlencode({
      serviceAccount = {
        create = true
        name   = "cloudwatch-agent"
        annotations = {
          "eks.amazonaws.com/role-arn" = module.cloudwatch_observability_irsa.iam_role_arn
        }
      }

      cloudWatchLogs = {
        enabled         = true
        region          = var.region
        logGroupName    = "/aws/containerinsights/${module.eks.cluster_name}/application"
        logStreamPrefix = "fluent-bit-"
        autoCreateGroup = false
      }

      firehose = {
        enabled = false
      }

      kinesis = {
        enabled = false
      }

      elasticsearch = {
        enabled = false
      }

      # Collect logs from all containers
      input = {
        enabled         = true
        tag             = "kube.*"
        path            = "/var/log/containers/*.log"
        db              = "/var/log/flb_kube.db"
        multilineParser = "docker, cri"
        memBufLimit     = "5MB"
        skipLongLines   = "On"
        refreshInterval = "10"
      }

      # Enrich logs with Kubernetes metadata
      filter = {
        enabled           = true
        match             = "kube.*"
        kubeURL           = "https://kubernetes.default.svc.cluster.local:443"
        mergeLog          = "On"
        mergeLogKey       = "data"
        keepLog           = "On"
        k8sLoggingParser  = "On"
        k8sLoggingExclude = "Off"
        bufferSize        = "32k"
      }

      # Route logs to application-specific log groups based on container names
      # Log path format: /var/log/containers/<pod>_<namespace>_<container>-<id>.log
      # Tag format after processing: kube.var.log.containers.<pod>_<namespace>_<container>-<id>.log
      additionalOutputs = <<-EOT
        [OUTPUT]
            Name              cloudwatch_logs
            Match             kube.var.log.containers.kaban-backend-*_kaban_backend-*
            region            ${var.region}
            log_group_name    /kaban/${var.environment}/backend
            log_stream_prefix backend-
            auto_create_group false
            retry_limit       2

        [OUTPUT]
            Name              cloudwatch_logs
            Match             kube.var.log.containers.kaban-backend-celery-worker-*_kaban_celery-worker-*
            region            ${var.region}
            log_group_name    /kaban/${var.environment}/celery
            log_stream_prefix celery-
            auto_create_group false
            retry_limit       2

        [OUTPUT]
            Name              cloudwatch_logs
            Match             kube.var.log.containers.kaban-frontend-*_kaban_frontend-*
            region            ${var.region}
            log_group_name    /kaban/${var.environment}/frontend
            log_stream_prefix frontend-
            auto_create_group false
            retry_limit       2
      EOT
    })
  ]

  depends_on = [
    module.eks,
    kubernetes_namespace_v1.amazon_cloudwatch,
    module.cloudwatch_observability_irsa,
    aws_cloudwatch_log_group.kaban_backend,
    aws_cloudwatch_log_group.kaban_celery,
    aws_cloudwatch_log_group.kaban_frontend
  ]
}
