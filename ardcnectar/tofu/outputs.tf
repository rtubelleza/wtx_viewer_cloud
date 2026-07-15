output "vm_ip" {
  description = "Public (qld) IP of the viewer instance."
  value = local.vm_ip
}

output "app_url" {
  description = "HTTPS URL the viewer is served at."
  value = "https://${local.app_fqdn}"
}

output "ssh_command" {
  description = "Convenience SSH command (uses the generated deploy key below)."
  value = "ssh ubuntu@${local.vm_ip}"
}

# manual retrieval for staging:
# tofu output -raw ssh_private_key > deploy_key && chmod 600 deploy_key
output "ssh_private_key" {
  description = "Generated ed25519 private key for the deploy/admin user."
  value = tls_private_key.deploy.private_key_openssh
  sensitive = true
}
