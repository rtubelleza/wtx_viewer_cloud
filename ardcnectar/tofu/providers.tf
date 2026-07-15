provider "openstack" {} # read OS_* vars for auth

provider "tls" {}

provider "github" {
  owner = var.github_owner
}
