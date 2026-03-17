import os
from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client
from swiftclient import Connection
from novaclient import client as nvc
from designateclient.v2 import client as dnc
import openstack

NOVA_VERSION = "2"

def get_current_instance_ip():
    ip = os.environ["SSH_CONNECTION"].split(" ")[-2] # port is -1, then second is host
    return ip

def validate_openstack_user_cred():
    required_creds = [
        "OS_AUTH_URL",
        "OS_USERNAME",
        "OS_PASSWORD",
        "OS_USER_DOMAIN_NAME",
        "OS_PROJECT_NAME",
        "OS_PROJECT_DOMAIN_ID"
    ]
    for x in required_creds:
        if x not in os.environ:
            raise KeyError(f"{x} not in environment variables")

def get_keystone_user_auth():
    validate_openstack_user_cred()
    auth = v3.Password(
        auth_url=os.environ["OS_AUTH_URL"],
        username=os.environ["OS_USERNAME"],
        password=os.environ["OS_PASSWORD"],
        user_domain_name=os.environ["OS_USER_DOMAIN_NAME"],
        project_name=os.environ["OS_PROJECT_NAME"],
        project_domain_name=os.environ["OS_PROJECT_DOMAIN_ID"],
    )
    return auth

def validate_openstack_app_cred():
    required_creds = [
        "OS_AUTH_URL",
        "OS_APPLICATION_CREDENTIAL_ID",
        "OS_APPLICATION_CREDENTIAL_SECRET"
    ]
    for x in required_creds:
        if x not in os.environ:
            raise KeyError(f"{x} not in environment variables")

def get_keystone_app_auth():
    validate_openstack_app_cred()
    auth = v3.ApplicationCredential(
        auth_url=os.environ["OS_AUTH_URL"],
        application_credential_id=os.environ["OS_APPLICATION_CREDENTIAL_ID"],
        application_credential_secret=os.environ["OS_APPLICATION_CREDENTIAL_SECRET"],
    )
    return auth

def get_keystone_session(how="user"):
    if how == "user":
        auth = get_keystone_user_auth()
    elif how == "app":
        auth = get_keystone_app_auth()
    else:
        raise ValueError(f"{how} not a valid option. Options: ['user', 'app'].")

    return session.Session(auth=auth)

def get_keystone_client(how="user"):
    session = get_keystone_session(how)
    return client.Client(session=session)

def get_swift_connection(how="user"):
    session = get_keystone_session(how)
    return Connection(session=session)

def get_novaclient():
    user_session = get_keystone_session("user") # must be user
    return nvc.Client(NOVA_VERSION, session=user_session)

def get_designateclient():
    user_session = get_keystone_session("user") # must be user
    return dnc.Client(session=user_session)

def get_openstackconnection():
    user_session = get_keystone_session("user") # must be user
    return openstack.connection.Connection(session=user_session)