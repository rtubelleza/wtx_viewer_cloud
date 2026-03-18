#!/bin/sh

# check required openstack env vars
for var in OS_AUTH_URL OS_APPLICATION_CREDENTIAL_ID OS_APPLICATION_CREDENTIAL_SECRET OS_PROJECT_ID; do
  eval val=\$$var
  if [ -z "$val" ]; then
    echo "ERROR: $var is not set" >&2
    exit 1
  fi
  echo "$var=${val:0:8}..."
done

SWIFT_STORAGE_URL="https://object-store.rc.nectar.org.au/v1/AUTH_${OS_PROJECT_ID}"
export SWIFT_STORAGE_URL

# fetch swift token and put in /tmp of running instance/container
fetch_token() {
  HTTP_CODE=$(curl -s -X POST "${OS_AUTH_URL}auth/tokens" \
    -H "Content-Type: application/json" \
    -d "{\"auth\":{\"identity\":{\"methods\":[\"application_credential\"],\"application_credential\":{\"id\":\"${OS_APPLICATION_CREDENTIAL_ID}\",\"secret\":\"${OS_APPLICATION_CREDENTIAL_SECRET}\"}}}}" \
    -D /tmp/swift_headers \
    -o /tmp/swift_body \
    -w "%{http_code}")

  if [ "$HTTP_CODE" != "201" ]; then
    echo "ERROR: Keystone returned HTTP $HTTP_CODE" >&2
    cat /tmp/swift_body >&2
    return 1
  fi

  grep -i "^x-subject-token:" /tmp/swift_headers | awk '{print $2}' | tr -d '\r\n'
}

# set storage url to config of data_store serv
write_config() {
  SWIFT_AUTH_TOKEN="$1" envsubst '${SWIFT_AUTH_TOKEN} ${SWIFT_STORAGE_URL}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf
}

echo "Fetching initial Swift auth token from ${OS_AUTH_URL}..."
TOKEN=$(fetch_token)
if [ $? -ne 0 ] || [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to fetch Swift auth token" >&2
  exit 1
fi

echo "Token acquired, starting nginx server..."
write_config "$TOKEN"
nginx
trap "nginx -s quit; exit 0" TERM INT

# refresh swift token every X s, for now refresh every 3000seconds
while true; do
  sleep 3000 &
  wait $!
  echo "Refreshing Swift auth token..."
  TOKEN=$(fetch_token)
  if [ $? -eq 0 ] && [ -n "$TOKEN" ]; then
    write_config "$TOKEN"
    nginx -s reload
    echo "Token refreshed."
  else
    echo "WARNING: Failed to refresh token, keeping existing." >&2
  fi
done
