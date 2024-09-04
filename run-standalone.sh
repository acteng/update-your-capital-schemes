#!/bin/bash

set -e -m

APP_SERVER_HOST=127.0.0.1
APP_SERVER_PORT=5000
APP_API_KEY=$(openssl rand -hex 32)
OIDC_SERVER_HOST=localhost
OIDC_SERVER_PORT=5001
OIDC_CLIENT_ID=schemes
USER_ID=boardman
USER_EMAIL=boardman@example.com
AUTHORITY_ID=1
AUTHORITY_NAME="Liverpool City Region Combined Authority"

# Generate key pair

OIDC_CLIENT_PRIVATE_KEY=$(openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048)
OIDC_CLIENT_PUBLIC_KEY=$(echo "${OIDC_CLIENT_PRIVATE_KEY}" | openssl rsa -pubout)

# Run stub OIDC server

FLASK_SERVER_NAME=${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT} \
flask \
	--app tests.e2e.oidc_server.app \
	run \
	--port ${OIDC_SERVER_PORT} \
	&

OIDC_SERVER_PID=$!
trap "kill ${OIDC_SERVER_PID}" EXIT

# Register OIDC client

curl http://${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT}/clients \
	--retry 5 \
	--retry-connrefused \
	-H 'Content-Type: application/json' \
	-d "{
			\"client_id\": \"${OIDC_CLIENT_ID}\",
			\"redirect_uri\": \"http://${APP_SERVER_HOST}:${APP_SERVER_PORT}/auth\",
			\"public_key\": \"${OIDC_CLIENT_PUBLIC_KEY//$'\n'/\\n}\",
			\"scope\": \"openid email\"
		}"

# Create user

curl http://${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT}/users \
	-H 'Content-Type: application/json' \
	-d "{\"id\": \"${USER_ID}\", \"email\": \"${USER_EMAIL}\"}"

# Run app server

FLASK_SERVER_NAME="${APP_SERVER_HOST}:${APP_SERVER_PORT}" \
FLASK_SESSION_COOKIE_SECURE=false \
FLASK_API_KEY=${APP_API_KEY} \
FLASK_GOVUK_SERVER_METADATA_URL="http://${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT}/.well-known/openid-configuration" \
FLASK_GOVUK_TOKEN_ENDPOINT="http://${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT}/token" \
FLASK_GOVUK_END_SESSION_ENDPOINT="http://${OIDC_SERVER_HOST}:${OIDC_SERVER_PORT}/logout" \
FLASK_GOVUK_CLIENT_ID=${OIDC_CLIENT_ID} \
FLASK_GOVUK_CLIENT_SECRET=${OIDC_CLIENT_PRIVATE_KEY} \
flask \
	--app schemes \
	run \
	--port ${APP_SERVER_PORT} \
	&

# Load app data

curl http://${APP_SERVER_HOST}:${APP_SERVER_PORT}/authorities \
	--retry 5 \
	--retry-connrefused \
	-H 'Content-Type: application/json' \
	-H "Authorization: API-Key ${APP_API_KEY}" \
	-d "[{\"id\": ${AUTHORITY_ID}, \"name\": \"${AUTHORITY_NAME}\"}]"

curl http://${APP_SERVER_HOST}:${APP_SERVER_PORT}/authorities/${AUTHORITY_ID}/users \
	-H 'Content-Type: application/json' \
	-H "Authorization: API-Key ${APP_API_KEY}" \
	-d "[{\"email\": \"${USER_EMAIL}\"}]"

curl http://${APP_SERVER_HOST}:${APP_SERVER_PORT}/schemes \
	-H 'Content-Type: application/json' \
	-H "Authorization: API-Key ${APP_API_KEY}" \
	-d "[
			{
				\"id\": 123,
				\"reference\": \"ATE00123\",
				\"overview_revisions\": [
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"name\": \"School Streets\",
						\"authority_id\": ${AUTHORITY_ID},
						\"type\": \"construction\",
						\"funding_programme\": \"ATF4\"
					}
				],
				\"bid_status_revisions\": [
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"status\": \"funded\"
					}
				],
				\"financial_revisions\": [
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"type\": \"funding allocation\",
						\"amount\": 500000,
						\"source\": \"Pulse 6\"
					},
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"type\": \"spend to date\",
						\"amount\": 400000,
						\"source\": \"Pulse 6\"
					}
				],
				\"milestone_revisions\": [
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"milestone\": \"feasibility design completed\",
						\"observation_type\": \"Planned\",
						\"status_date\": \"2021-01-01\",
						\"source\": \"Pulse 6\"
					}
				],
				\"output_revisions\": [
					{
						\"effective_date_from\": \"2020-01-01T00:00:00\",
						\"effective_date_to\": null,
						\"type\": \"New segregated cycling facility\",
						\"measure\": \"number of junctions\",
						\"value\": \"1.000000\",
						\"observation_type\": \"Planned\"
					}
				],
				\"authority_reviews\": [
					{
						\"review_date\": \"2020-01-01T00:00:00\",
						\"source\": \"Pulse 6\"
					}
				]
			}
		]"

# Foreground app server

fg
