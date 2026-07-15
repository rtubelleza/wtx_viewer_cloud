# push the CI/CD deploy key + VM IP to GitHub Actions
# CD workflow SSHes in, private half of the keypair generated in compute.tf
resource "github_actions_secret" "ssh_private_key" {
  count = var.manage_github_secrets ? 1 : 0 # 1: prod, 0: staging
  repository = var.github_repository
  secret_name = "SSH_PRIVATE_KEY"
  value = tls_private_key.deploy.private_key_openssh
}

# Target host for CD SSH
resource "github_actions_secret" "vm_ip" {
  count = var.manage_github_secrets ? 1 : 0
  repository = var.github_repository
  secret_name = "VM_IP"
  value = local.vm_ip
}

# Public key 
resource "github_actions_variable" "ssh_public_key" {
  count = var.manage_github_secrets ? 1 : 0
  repository = var.github_repository
  variable_name = "SSH_PUBLIC_KEY"
  value = tls_private_key.deploy.public_key_openssh
}
