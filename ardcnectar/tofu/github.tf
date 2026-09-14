# CI/CD deploy key + VM IP live on a GitHub Environment, not on the repository.
# The environment is also the approval gate: its reviewers must click before the
# deploy job runs. Secret names are unchanged; GitHub resolves them per
# environment for any job that declares `environment:`.
resource "github_repository_environment" "deploy" {
  count       = var.manage_github_secrets ? 1 : 0 # 1: prod, 0: staging
  repository  = var.github_repository
  environment = var.github_environment

  # The gate. Empty sets mean no approval is required.
  reviewers {
    users = var.github_environment_reviewer_users
    teams = var.github_environment_reviewer_teams
  }
}

# CD workflow SSHes in, private half of the keypair generated in compute.tf
resource "github_actions_environment_secret" "ssh_private_key" {
  count       = var.manage_github_secrets ? 1 : 0
  repository  = var.github_repository
  environment = github_repository_environment.deploy[0].environment
  secret_name = "SSH_PRIVATE_KEY"
  value       = tls_private_key.deploy.private_key_openssh
}

# Target host for CD SSH
resource "github_actions_environment_secret" "vm_ip" {
  count       = var.manage_github_secrets ? 1 : 0
  repository  = var.github_repository
  environment = github_repository_environment.deploy[0].environment
  secret_name = "VM_IP"
  value       = local.vm_ip
}

# Public key - not a secret, stays repository-scoped
resource "github_actions_variable" "ssh_public_key" {
  count         = var.manage_github_secrets ? 1 : 0
  repository    = var.github_repository
  variable_name = "SSH_PUBLIC_KEY"
  value         = tls_private_key.deploy.public_key_openssh
}
