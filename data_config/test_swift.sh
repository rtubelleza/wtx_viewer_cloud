#!/bin/sh
# Tests direct connectivity from data_store to Swift object storage.
# Usage:
#   ./data_config/test_swift.sh                          # uses /opt/wtx_viewer/app_credentials.env
#   ENV_FILE=/path/to/creds.env ./data_config/test_swift.sh
#   docker exec <data_store_container> /bin/sh -c "$(cat data_config/test_swift.sh)"

set -e

ENV_FILE="${ENV_FILE:-/opt/wtx_viewer/app_credentials.env}"

# Load credentials if not already in environment
if [ -z "$OS_AUTH_URL" ]; then
  if [ -f "$ENV_FILE" ]; then
    echo "Loading credentials from $ENV_FILE"
    # shellcheck disable=SC1090
    set -a; . "$ENV_FILE"; set +a
  else
    echo "ERROR: $ENV_FILE not found and OS_AUTH_URL not set" >&2
    exit 1
  fi
fi

# Validate required vars
MISSING=0
for var in OS_AUTH_URL OS_APPLICATION_CREDENTIAL_ID OS_APPLICATION_CREDENTIAL_SECRET OS_PROJECT_ID; do
  eval val=\$$var
  if [ -z "$val" ]; then
    echo "FAIL  env var $var is not set" >&2
    MISSING=1
  else
    echo "OK    $var=${val:0:8}..."
  fi
done
[ "$MISSING" -eq 1 ] && exit 1

SWIFT_STORAGE_URL="https://object-store.rc.nectar.org.au/v1/AUTH_${OS_PROJECT_ID}"
echo ""
echo "--- Test 1: Keystone token ---"
HTTP_CODE=$(curl -s -X POST "${OS_AUTH_URL}auth/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"auth\":{\"identity\":{\"methods\":[\"application_credential\"],\"application_credential\":{\"id\":\"${OS_APPLICATION_CREDENTIAL_ID}\",\"secret\":\"${OS_APPLICATION_CREDENTIAL_SECRET}\"}}}}" \
  -D /tmp/swift_test_headers \
  -o /tmp/swift_test_body \
  -w "%{http_code}")

if [ "$HTTP_CODE" != "201" ]; then
  echo "FAIL  Keystone returned HTTP $HTTP_CODE (expected 201)" >&2
  cat /tmp/swift_test_body >&2
  exit 1
fi
TOKEN=$(grep -i "^x-subject-token:" /tmp/swift_test_headers | awk '{print $2}' | tr -d '\r\n')
echo "OK    Token acquired (${TOKEN:0:8}...)"

echo ""
echo "--- Test 2: Swift container reachable ---"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "X-Auth-Token: $TOKEN" \
  "${SWIFT_STORAGE_URL}/main")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
  echo "OK    Container /main responded HTTP $HTTP_CODE"
else
  echo "FAIL  Container /main responded HTTP $HTTP_CODE (expected 200 or 204)" >&2
  exit 1
fi

echo ""
echo "--- Test 3: Zarr root reachable ---"
# Try the zarr .zgroup at the root of the store
TEST_PATH="${SWIFT_STORAGE_URL}/main/mosaic.zarr/.zgroup"
HTTP_CODE=$(curl -s -o /tmp/swift_zarr_resp -w "%{http_code}" \
  -H "X-Auth-Token: $TOKEN" \
  "$TEST_PATH")
if [ "$HTTP_CODE" = "200" ]; then
  echo "OK    $TEST_PATH responded HTTP 200"
  echo "      Content: $(cat /tmp/swift_zarr_resp)"
else
  echo "FAIL  $TEST_PATH responded HTTP $HTTP_CODE" >&2
  cat /tmp/swift_zarr_resp >&2
  exit 1
fi

echo ""
echo "All Swift connectivity tests passed."
