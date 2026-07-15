terraform {
  # opentofu cli version
  required_version = ">= 1.7.0" # version for GA supported encrpytion

  required_providers {
    # nectar stack
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "~> 3.0" # any 3.x but not 4.0
    }
    # Generates the ed25519 SSH keypair in-config.
    tls = {
      source = "hashicorp/tls"
      version = "~> 4.0"
    }
    # Manages GitHub Actions secrets/variables (prod only; skipped in staging).
    github = {
      source = "integrations/github"
      version = "~> 6.0"
    }
  }

  # below must exist/bootstrapped already
  backend "s3" {
    bucket = "wtx-viewer-tfstate" # swift container
    # key omitted, explicitly supplied in cli
    #   tofu init -backend-config="key=staging/terraform.tfstate"
    #   tofu init -backend-config="key=prod/terraform.tfstate"
    endpoints = { s3 = "https://swift.rc.nectar.org.au/" }
    region = "us-east-1" # RGW default, ignorede in this setup

    # skip aws
    skip_credentials_validation = true
    skip_region_validation = true
    skip_requesting_account_id = true
    skip_metadata_api_check = true
    use_path_style = true # Ceph RGW requires path-style URLs
    # use_lockfile = true
  }

  # encrypt tf state
  encryption {
    key_provider "pbkdf2" "state" {
      passphrase = var.state_encryption_passphrase
    }
    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.state
    }
    state {
      method = method.aes_gcm.state
    }
    plan {
      method = method.aes_gcm.state
    }
  }
}
