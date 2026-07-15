data "openstack_identity_auth_scope_v3" "current" {
  name = "wtx-viewer-scope"
}

# creates member-scoped application credential in Keystone. 
# secret injected via cloud-init
resource "openstack_identity_application_credential_v3" "app" {
  name = var.instance_name
  description = "wtx viewer data_store Swift access (${var.instance_name})"
  roles = ["member", "reader"]

  access_rules {
    service = "object-store"
    method = "GET"
    path = "/v1/AUTH_${data.openstack_identity_auth_scope_v3.current.project_id}/main/**"
  }
}
