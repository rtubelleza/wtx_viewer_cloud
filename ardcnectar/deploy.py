"""
Deploy a Nectar container instance with wtx_viewer running.
Requires user OpenStack credentials in environment (source openrc or vars from .env).
"""
import subprocess
import time
import os
from pathlib import Path

import yaml
import openstack
import auth
from keystoneauth1.exceptions import NotFound
from jinja2 import Template

CONFIG_FILE = "./instance_config.yaml" # Defins 
CLOUD_INIT = "./cloud_init.yaml"
SG_NAME = "viewer_ingress"

def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def render_cloud_init() -> str:
    with open(CLOUD_INIT) as f:
        template = Template(f.read())

    # substitute env vars
    cloud_init_instantiated = template.render(
        OS_AUTH_URL=os.environ["OS_AUTH_URL"],
        OS_USERNAME=os.environ["OS_USERNAME"],
        OS_PASSWORD=os.environ["OS_PASSWORD"],
        OS_PROJECT_ID=os.environ["OS_PROJECT_ID"],
        OS_USER_DOMAIN_NAME=os.environ["OS_USER_DOMAIN_NAME"],
        OS_PROJECT_DOMAIN_ID=os.environ["OS_PROJECT_DOMAIN_ID"],
        OS_PROJECT_NAME=os.environ["OS_PROJECT_NAME"],
    )
    
    return cloud_init_instantiated

# def ensure_http_security_group() -> str:
#     conn = auth.get_openstackconnection()
#     existing_sgs = {sg.name: sg for sg in conn.network.security_groups()}

#     if SG_NAME not in existing_sgs:
#         sg = conn.network.create_security_group(
#             name=SG_NAME, 
#             description="Allow public ingress"
#         )
#         conn.network.create_security_group_rule(
#             sg.id,
#             direction="ingress",
#             protocol="tcp",
#             port_range_min=80,
#             port_range_max=80,
#             remote_ip_prefix="0.0.0.0/0",
#         )
#         print(f"Created security group '{SG_NAME}' with TCP port 80 open.")
#     else:
#         print(f"Security group '{SG_NAME}' already exists.")

#     return SG_NAME

def deploy_server():
    cfg = load_config() #./instance_config.yaml
    instance = cfg["instance"]

    # http_sg = ensure_http_security_group()
    # security_groups = instance["security_groups"] + [http_sg]
    security_groups = instance["security_groups"]

    # novaclient api for server creation
    nova = auth.get_novaclient()

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
        userdata=render_cloud_init(),
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

def expose_app(server_ip):
    # add container server as a record set to the project alloc DNS
    # type A = Address record
    # records; IP of container server
    dns_client = auth.get_designateclient()
    zones = dns_client.zones.list()
    
    TARGET_ZONE = "nsclc-spatial-atlas.cloud.edu.au."
    APP_DOMAIN = "viewer." + TARGET_ZONE
    TIME_TO_LIVE = 300 # 300s; TODO: change to higher numbers later
    
    zone = next(z for z in zones if z["name"] == TARGET_ZONE)
    zone_id = zone["id"]
    dns_client.recordsets.create(
        zone_id,
        name=APP_DOMAIN,
        type_="A",
        records=[server_ip],
        ttl=TIME_TO_LIVE
    )

    print(
        f"Added Address Record Set: {APP_DOMAIN} to {TARGET_ZONE}"
    )
    print(
        f"Record Set: {APP_DOMAIN} points to {server_ip}"
    )

def main():
    # check necessary user env vars exist as user
    auth.validate_openstack_user_cred()

    # create server container instance, build and launch viewer_app
    server = deploy_server()
    server_ip = server.networks["qld"][0]

    # expose viewer_app, access with DNS
    expose_app(server_ip)


if __name__ == "__main__":
    main()
