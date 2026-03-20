import yaml
import auth
from keystoneauth1.exceptions import NotFound
from novaclient import exceptions as nova_exc


CONFIG_FILE = "./instance_config.yaml"


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def delete_server(nova, instance_name: str):
    try:
        server = nova.servers.find(name=instance_name)
        nova.servers.delete(server)
        print(f"Deleted compute instance '{instance_name}'.")
    except nova_exc.NotFound:
        print(f"Compute instance '{instance_name}' not found, skipping.")


def delete_dns_record(dns_client, target_zone: str, app_domain: str):
    zones = dns_client.zones.list()

    zone = next((z for z in zones if z["name"] == target_zone), None)
    if zone is None:
        print(f"DNS zone '{target_zone}' not found, skipping.")
        return

    zone_id = zone["id"]
    recordsets = dns_client.recordsets.list(zone_id)
    record = next(
        (rs for rs in recordsets if rs["name"] == app_domain and rs["type"] == "A"),
        None,
    )
    if record is None:
        print(f"DNS A record '{app_domain}' not found in zone '{target_zone}', skipping.")
        return

    dns_client.recordsets.delete(zone_id, record["id"])
    print(f"Deleted DNS A record '{app_domain}' from zone '{target_zone}'.")


def delete_app_credentials(keystone, instance_name: str):
    try:
        app_cred = keystone.application_credentials.find(name=instance_name)
        keystone.application_credentials.delete(app_cred)
        print(f"Deleted application credentials '{instance_name}'.")
    except NotFound:
        print(f"Application credentials '{instance_name}' not found, skipping.")

def delete_github_actions_keypair():
    pass

def main():
    dns_client = auth.get_designateclient()
    nova = auth.get_novaclient()
    user_keystone = auth.get_keystone_client("user")

    cfg = load_config()
    instance_name = cfg["instance"]["name"]
    target_zone = cfg["app"]["target_zone"]
    app_domain = cfg["app"]["app_domain"]

    print(f"Tearing down '{instance_name}'...")

    delete_server(nova, instance_name)
    delete_dns_record(dns_client, target_zone, app_domain)
    delete_app_credentials(user_keystone, instance_name)
    print("Teardown complete.")

if __name__ == "__main__":
    main()
