# Maintenance

Project dependencies should be kept up-to-date for the latest security fixes.

## Upgrading Python packages

To list Python packages that need upgrading:

```bash
pip list --outdated
```

To upgrade local packages to their latest patch versions:

```bash
pip install --force-reinstall -e .[dev]
```

To upgrade packages to their latest minor or major version:

1. Bump the package version in `pyproject.toml` keeping the patch version zero, e.g. `~=1.2.0` to `~=1.3.0`

1. Install the upgraded packages:

   ```bash
   pip install -e .[dev]
   ```

## Upgrading Node packages

To list Node packages that need upgrading:

```bash
npm outdated
```

To upgrade packages to their latest patch versions:

```bash
npm upgrade
```

### Upgrading GOV.UK One Login Server Header package

This dependency uses a [GitHub URL](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#github-urls) as it
hasn't been released yet. To upgrade:

1. Update the commit hash for the dependency `govuk-one-login-service-header` in `package.json` to the
   [latest commit](https://github.com/govuk-one-login/service-header/commits/main/)

1. Copy the contents of
   [the service header Nunjucks template](https://raw.githubusercontent.com/govuk-one-login/service-header/main/src/nunjucks/template.njk)
   to `schemes/views/templates/govuk_one_login_service_header/macro.html`, replacing the contents of the Jinja macro:

   ```
   {% macro govukOneLoginServiceHeader(params) %}

   <PASTE HERE>

   {% endmacro %}
   ```

## Upgrading Terraform providers

Upgrade each Terraform root module in `cloud`:

1. Upgrade the providers in `versions.tf` to the latest minor or major version keeping the patch version zero,
   e.g. `~> 1.2.0` to `~> 1.3.0`

1. Install the upgraded providers:

   ```bash
   terraform init -upgrade
   ```
