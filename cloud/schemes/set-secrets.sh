#!/bin/bash

# Sets the environment secrets in Google Secret Manager

set -eo pipefail

if [ $# -ne 1 ]
then
	echo "Usage: set-secrets.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1
PROJECT="dft-schemes-${ENVIRONMENT}"

BASIC_AUTH_ITEM=$(bw get item "uycs-basic-auth-${ENVIRONMENT}" || true)
if [ -n "${BASIC_AUTH_ITEM}" ]; then
	echo "${BASIC_AUTH_ITEM}" | jq -r '.login.username' \
		| gcloud secrets create "basic-auth-username" --project "${PROJECT}" --data-file=-

	echo "${BASIC_AUTH_ITEM}" | jq -r '.login.password' \
		| gcloud secrets create "basic-auth-password" --project "${PROJECT}" --data-file=-
fi

bw get notes "uycs-govuk-one-login-private-key-${ENVIRONMENT}" \
	| gcloud secrets create "govuk-client-secret" --project "${PROJECT}" --data-file=-

bw get notes "uycs-ate-api-private-key-${ENVIRONMENT}" \
	| gcloud secrets create "ate-api-client-secret" --project "${PROJECT}" --data-file=-
