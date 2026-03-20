import auth
import os

def main():
    user_client = auth.get_keystone_client("user")
    APP_CRED_NAME = os.environ["INSTANCE_NAME"]
    OS_PROJECT_ID = os.environ["OS_PROJECT_ID"]

    app_cred = user_client.application_credentials.create(
        name=APP_CRED_NAME,
        roles=[{"name": "Member"}]
    )

    app_cred_dict = app_cred.to_dict()

    # captured in shell to .env file by script
    print("OS_AUTH_URL=https://keystone.rc.nectar.org.au/v3/")
    print(f"OS_PROJECT_ID={OS_PROJECT_ID}")
    print(f"OS_APPLICATION_CREDENTIAL_ID={app_cred_dict['id']}")
    print(f"OS_APPLICATION_CREDENTIAL_SECRET={app_cred_dict['secret']}")

if __name__ == "__main__":
    main()