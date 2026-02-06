#!/bin/bash

# Gets the local environment variables from Bitwarden

set -eo pipefail

cat <<EOF >.env
FLASK_SECRET_KEY=$(bw get password uycs-secret-key-local)
FLASK_API_KEY=$(bw get password uycs-api-key-local)
FLASK_GOVUK_CLIENT_SECRET="$(bw get notes uycs-govuk-one-login-private-key-dev | sed -z 's/\n/\\n/g')"
#FLASK_ATE_URL=https://dev.api.activetravelengland.gov.uk
#FLASK_ATE_CLIENT_ID=$(bw get username uycs-ate-api-client-dev)
#FLASK_ATE_CLIENT_SECRET="$(bw get notes uycs-ate-api-private-key-dev | sed -z 's/\n/\\n/g')"
#FLASK_ATE_SERVER_METADATA_URL=https://dev.identity.api.activetravelengland.gov.uk/.well-known/openid-configuration
#FLASK_ATE_AUDIENCE=https://dev.api.activetravelengland.gov.uk
EOF
