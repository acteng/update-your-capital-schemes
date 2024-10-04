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

## Creating a cold backup

To download the latest database backup for storing offline:

```bash
./cold-backup.sh $ENVIRONMENT
```

This will create a compressed PostgreSQL custom-format archive `schemes-$ENVIRONMENT.dump.gz`.

## Restoring a cold backup

To restore a backup to a local or proxied database:

1. Uncompress the archive:

   ```bash
   gunzip schemes-$ENVIRONMENT.dump.gz
   ```

1. Restore the backup:

   ```bash
   docker run --rm -i \
       --network=host \
       -e PGUSER=schemes \
       -e PGPASSWORD=$PGPASSWORD \
       postgres:16 \
       pg_restore -h localhost -d schemes --no-owner < schemes-$ENVIRONMENT.dump
   ```
