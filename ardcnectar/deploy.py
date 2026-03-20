"""
Deploy a Nectar container instance with wtx_viewer running.
Requires user OpenStack credentials in environment (source openrc or vars from .env).
Requires gh CLI authenticated (gh auth login) to push secrets to GitHub.

Should currently only be run as local user.
"""

import subprocess
import tempfile
import time
import os
from pathlib import Path

import yaml
import auth
from jinja2 import Template

CONFIG_FILE = "./instance_config.yaml"
CLOUD_INIT = "./cloud_init.yaml"


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def render_cloud_init(app_domain, admin_email, gh_actions_public_key: str) -> str:
    with open(CLOUD_INIT) as f:
        template = Template(f.read())

    cloud_init_instantiated = template.render(
        OS_AUTH_URL=os.environ["OS_AUTH_URL"],
        OS_USERNAME=os.environ["OS_USERNAME"],
        OS_PASSWORD=os.environ["OS_PASSWORD"],
        OS_PROJECT_ID=os.environ["OS_PROJECT_ID"],
        OS_USER_DOMAIN_NAME=os.environ["OS_USER_DOMAIN_NAME"],
        OS_PROJECT_DOMAIN_ID=os.environ["OS_PROJECT_DOMAIN_ID"],
        OS_PROJECT_NAME=os.environ["OS_PROJECT_NAME"],
        APP_DOMAIN=app_domain,
        ADMIN_EMAIL=admin_email,
        GH_ACTIONS_PUBLIC_KEY=gh_actions_public_key,
    )

    return cloud_init_instantiated


def setup_gh_actions_update_key(nova, gh_actions_key_name):
    nova = auth.get_novaclient()  # user client

    existing_keypair_names = [x.name for x in nova.keypairs.list()]

    # force recreate
    if gh_actions_key_name in existing_keypair_names:
        nova.keypairs.delete(gh_actions_key_name)
        subprocess.run(["gh", "secret", "delete", "SSH_PRIVATE_KEY"])

    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir) / "deploy_key"

        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-C",
                gh_actions_key_name,
                "-f",
                str(key_path),
                "-N",
                "",
            ],
            check=True,
            capture_output=True,
        )

        private_key = key_path.read_text()
        public_key = key_path.with_suffix(".pub").read_text().strip()

    # upload public key to Nectar project
    nova.keypairs.create(name=gh_actions_key_name, public_key=public_key)
    print(f"Created Nectar keypair '{gh_actions_key_name}'")

    subprocess.run(
        ["gh", "secret", "set", "SSH_PRIVATE_KEY", "--body", private_key], check=True
    )
    print("Set GitHub secret SSH_PRIVATE_KEY")

    subprocess.run(
        ["gh", "variable", "set", "SSH_PUBLIC_KEY", "--body", public_key], check=True
    )
    print("Set GitHub variable SSH_PUBLIC_KEY")

    return public_key


def deploy_server(nova, app_domain, admin_email, gh_actions_public_key: str):
    cfg = load_config()
    instance = cfg["instance"]

    # http_sg = ensure_http_security_group()
    # security_groups = instance["security_groups"] + [http_sg]
    security_groups = instance["security_groups"]

    # get existing base image;
    image = nova.glance.find_image(instance["image"])
    flavor = nova.flavors.find(name=instance["flavor"])

    print(f"Creating instance '{instance['name']}'...")
    server = nova.servers.create(
        name=instance["name"],
        image=image,
        flavor=flavor,
        key_name=instance["key_name"],
        security_groups=security_groups,
        userdata=render_cloud_init(app_domain, admin_email, gh_actions_public_key),
    )

    # poll servr
    POLL_TIME_SECONDS = 4
    while True:
        server = nova.servers.get(server.id)
        print("Status: ", server.status)

        if server.status == "ACTIVE":
            print("Server active.")
            break

        if server.status == "ERROR":
            raise RuntimeError("Server failed to build.")

        time.sleep(POLL_TIME_SECONDS)

    return server


def expose_app(dns_client, target_zone, app_domain, ttl, server_ip):
    # add container server as a record set to the project alloc DNS
    # type A = Address record
    # records; IP of container server
    zones = dns_client.zones.list()

    zone = next(z for z in zones if z["name"] == target_zone)
    zone_id = zone["id"]
    dns_client.recordsets.create(
        zone_id, name=app_domain, type_="A", records=[server_ip], ttl=ttl
    )

    print(f"Added Address Record Set: {app_domain} to {target_zone}")
    print(f"Record Set: {app_domain} points to {server_ip}")


def main():
    # novaclient api for server creation
    nova = auth.get_novaclient()
    # dns_client to expose dns
    dns_client = auth.get_designateclient()

    cfg = load_config()
    app_domain = cfg["app"]["app_domain"].rstrip(
        "."
    )  # strip DNS trailing dot for HTTP URL
    admin_email = cfg["app"]["admin_email"]
    gh_actions_key_name = cfg["instance"]["github_actions_key"]

    # generate SSH keypair, upload to Nectar, push keys to GitHub
    gh_actions_public_key = setup_gh_actions_update_key(nova, gh_actions_key_name)

    # create server instance — public key injected into authorized_keys via cloud-init template
    server = deploy_server(nova, app_domain, admin_email, gh_actions_public_key)
    server_ip = server.networks["qld"][0]

    # expose viewer app via DNS
    app = cfg["app"]
    target_zone = app["target_zone"]
    app_domain = app["app_domain"]
    ttl = app["ttl"]
    expose_app(dns_client, target_zone, app_domain, ttl, server_ip)

    # push VM IP to gh secret so github-actions-update runner can ssh in
    subprocess.run(["gh", "secret", "set", "VM_IP", "--body", server_ip], check=True)
    print(f"Set GitHub secret VM_IP to {server_ip}")


if __name__ == "__main__":
    main()
