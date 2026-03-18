#!/bin/sh
# Tests the viewer_app proxy can serve zarr data (not index.html) from the data_store.
# Reads the zarr URL from vitessce_config/config.json and checks known zarr paths.
# Run from the repo root after `docker compose up`:
#   ./server_config/test_proxy.sh
#   BASE_URL=http://myhost:80 ./server_config/test_proxy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_JSON="${SCRIPT_DIR}/../vitessce_config/config.json"

# Extract the base zarr URL from config.json (first "url" value)
if command -v jq >/dev/null 2>&1; then
  RAW_URL=$(jq -r '[.. | objects | .url? | strings] | first' "$CONFIG_JSON")
else
  RAW_URL=$(grep -m1 '"url"' "$CONFIG_JSON" | sed 's/.*"url": *"\(.*\)".*/\1/')
fi

# Allow override via env
BASE_URL="${BASE_URL:-$RAW_URL}"

if [ -z "$BASE_URL" ]; then
  echo "ERROR: Could not determine base URL from $CONFIG_JSON" >&2
  exit 1
fi
echo "Testing zarr proxy at: $BASE_URL"
echo ""

FAIL=0

check() {
  LABEL="$1"
  URL="$2"
  EXPECTED_TYPE="${3:-application/}"  # partial match on Content-Type

  TMPFILE=$(mktemp)
  HTTP_CODE=$(curl -s -o "$TMPFILE" -w "%{http_code}" "$URL")
  CONTENT=$(cat "$TMPFILE")
  CTYPE=$(curl -s -o /dev/null -w "%{content_type}" "$URL")
  rm -f "$TMPFILE"

  # Fail if we got HTML (means it fell through to index.html)
  if echo "$CONTENT" | grep -qi "<!DOCTYPE html"; then
    echo "FAIL  [$LABEL] got HTML (index.html) — proxy not routing correctly"
    echo "      URL: $URL"
    FAIL=1
    return
  fi

  if [ "$HTTP_CODE" = "200" ]; then
    echo "OK    [$LABEL] HTTP 200  content-type: $CTYPE"
    echo "      URL: $URL"
  else
    echo "FAIL  [$LABEL] HTTP $HTTP_CODE"
    echo "      URL: $URL"
    echo "      Body: $CONTENT"
    FAIL=1
  fi
}

echo "--- Test 1: Zarr root (.zgroup) ---"
check "zarr root .zgroup" "${BASE_URL}/.zgroup"

echo ""
echo "--- Test 2: Zarr root (.zattrs) ---"
check "zarr root .zattrs" "${BASE_URL}/.zattrs"

echo ""
echo "--- Test 3: Range request (partial fetch) ---"
TMPFILE=$(mktemp)
HTTP_CODE=$(curl -s -o "$TMPFILE" -w "%{http_code}" \
  -H "Range: bytes=0-63" \
  "${BASE_URL}/.zgroup")
CONTENT=$(cat "$TMPFILE")
rm -f "$TMPFILE"

if echo "$CONTENT" | grep -qi "<!DOCTYPE html"; then
  echo "FAIL  [range request] got HTML — proxy not routing correctly"
  FAIL=1
elif [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "206" ]; then
  echo "OK    [range request] HTTP $HTTP_CODE"
else
  echo "FAIL  [range request] HTTP $HTTP_CODE — $CONTENT"
  FAIL=1
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "All proxy tests passed."
else
  echo "One or more proxy tests FAILED." >&2
  exit 1
fi
