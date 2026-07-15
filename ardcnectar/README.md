# Overview
Contains Infrastructure-as-Code for deploying the wtx_viewer in on Nectar using OpenTofu.
- Creates compute container instance
- Generates application credentials for that instance
- Registers container instance IP to project allocation zone as a record set
- Runs docker service in compute instance to host viewer application (see `data_config`, `server_config`, `vitessce_config`).

# Requirements
- OpenTofu
- OpenStack CLI

# Usage
## Environmental Variables
### 1. Source `OpenStack` env vars.
The following environmental variables need to be set for authentication:
| Variable | Description |
|---|---|
| `OS_AUTH_URL` | OpenStack Authentication URL. For Nectar Project allocations this is usually https://identity.rc.nectar.org.au/v3/|
| `OS_USERNAME` | OpenStack username/email. Usually member/tenantmember role. |
| `OS_PASSWORD` | OpenStack password. |
| `OS_PROJECT_ID` | OpenStack project ID for the allocation. |
| `OS_USER_DOMAIN_NAME` | OpenStack user domain name. Usually "Default". |
| `OS_PROJECT_DOMAIN_ID` | OpenStack project domain id. Usually "default". |
| `OS_PROJECT_NAME` | OpenStack project name. Usually the same name as the Nectar project allocation. |

It is recommended to set these automatiaclly from a `.env` file or by sourcing an OpenStack RC file (i.e. see https://tutorials.rc.nectar.org.au/openstack-cli/04-credentials).

### 2. Source S3 backend env vars.
The state of the deployment (.tfstate) is stored in an accompanying Swift Object store and is encrypted.
To store this, need the following env vars:
| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY` | "access" field |
| `AWS_SECRET_ACCESS_KEY` | "secret" field |
| `AWS_REGION` | Non-functional value, but used by Ceph RGW. Default to us-east-1. |
| `TF_VAR_state_encryption_passphrase` | any 20+ character passphrase |

Run `openstack ec2 credentials create`, and use the "access" and "secret" values for the two AWS env vars.

### 3. Source GitHub env vars.
| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | Github token for github secrets|

### 4. Create .tfvars specification in /tofu
This defines the deployment instances. Can create one called `prod.tfvars` and define the following variables
```terraform
instance_name = "my_instance"
app_domain = "myprefix.project-domain.cloud.edu.au"
admin_email = "admin@project-domain.cloud.edu.au"
manage_github_secrets = true

app_https_cidr = 0.0.0.0/0 # allow internet access to the app viewer
```

### 5. Run OpenTofu
```bash
tofu init -reconfigure -backend-config="key=prod/terraform.tfstate"
tofu plan  -var-file=prod.tfvars
tofu apply -var-file=prod.tfvars
```