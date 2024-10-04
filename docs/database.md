# Database

## Connecting to the database

1. Run the [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy) script:

   ```bash
   ./proxy.sh $ENVIRONMENT
   ```

1. Obtain the database password for the environment:

   ```bash
   gcloud secrets versions access latest --project dft-schemes-$ENVIRONMENT --secret database-password
   ```

1. Connect using PSQL and enter the password when prompted:

   ```bash
   psql -h localhost -U schemes schemes
   ```
