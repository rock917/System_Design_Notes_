terraform {
  required_version = ">= 1.5, < 2.0"
}

variable "environment" {
  type    = string
  default = "local-lab"
  validation {
    condition     = contains(["local-lab", "staging"], var.environment)
    error_message = "This educational example permits local-lab or staging labels only."
  }
}

# Built-in provider resource: no cloud resources or charges.
resource "terraform_data" "deployment_contract" {
  input = {
    environment = var.environment
    replicas    = 2
    image       = "shopstream-inference:local"
  }
}

output "reviewed_contract" {
  value = terraform_data.deployment_contract.output
}
