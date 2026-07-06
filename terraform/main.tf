terraform {
  required_version = ">= 1.0.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "devops-web-deployment"
}

locals {
  environments = {
    dev = {
      namespace = "web-dev"
      image     = "devops-web-deployment:dev"
      replicas  = 1
      node_port = 30081
    }

    qa = {
      namespace = "web-qa"
      image     = "devops-web-deployment:qa"
      replicas  = 1
      node_port = 30082
    }

    prod = {
      namespace = "web-prod"
      image     = "devops-web-deployment:prod"
      replicas  = 2
      node_port = 30083
    }
  }
}

resource "local_file" "environment_info" {
  for_each = local.environments

  filename = "${path.module}/generated/${each.key}-environment.txt"

  content = <<-EOT
  Proyecto: ${var.project_name}
  Ambiente: ${upper(each.key)}
  Namespace: ${each.value.namespace}
  Imagen Docker: ${each.value.image}
  Replicas: ${each.value.replicas}
  NodePort: ${each.value.node_port}
  Plataforma: Minikube
  EOT
}

output "configured_environments" {
  description = "Ambientes definidos por Terraform"

  value = {
    for environment, configuration in local.environments :
    environment => configuration.namespace
  }
}
