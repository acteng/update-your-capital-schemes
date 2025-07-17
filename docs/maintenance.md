# Maintenance

Project dependencies should be kept up-to-date for the latest security fixes.

## Upgrading GOV.UK Frontend

We use [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/) across the following packages:

* [GOV.UK Frontend Jinja Macros](https://github.com/LandRegistry/govuk-frontend-jinja) (Python)
* [GOV.UK Frontend WTF](https://github.com/LandRegistry/govuk-frontend-wtf) (Python)
* [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/) (Node)
* [GOV.UK One Login Service Header](https://github.com/govuk-one-login/service-header) (Node)

They should be aligned so that they all use the same version of GOV.UK Frontend.

The following sections detail how to upgrade some of these packages:

* [Upgrading GOV.UK Frontend Jinja Macros package](#upgrading-govuk-frontend-jinja-macros-package)
* [Upgrading GOV.UK One Login Service Header package](#upgrading-govuk-one-login-service-header-package)

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

1. Bump the package version in [pyproject.toml](../pyproject.toml) keeping the patch version zero, e.g. `~=1.2.0` to `~=1.3.0`

1. Install the upgraded packages:

   ```bash
   pip install -e .[dev]
   ```

### Upgrading GOV.UK Frontend Jinja Macros package

GOV.UK Frontend [doesn't allow the crown logo to be customised in the header](https://github.com/alphagov/govuk-frontend/issues/1639),
so we maintain a copy of the template to replace it with the ATE logo.

After upgrading GOV.UK Frontend Jinja Macros, update the template:

1. Copy the contents of [the header template](https://raw.githubusercontent.com/LandRegistry/govuk-frontend-jinja/refs/heads/main/govuk_frontend_jinja/templates/components/header/macro.html)
   to [schemes/views/templates/ate_header/macro.html](../schemes/views/templates/ate_header/macro.html) and rename the
   macro by applying the following patch:

   ```diff
   -{% macro govukHeader(params) %}
   +{% macro ateHeader(params) %}
   ```

1. Replace the crown logo with the ATE logo by applying the following patch:

   ```diff
   -        {{ govukLogo({
   -          'classes': "govuk-header__logotype",
   -          'ariaLabelText': "GOV.UK",
   -          'useTudorCrown': params.useTudorCrown,
   -          'rebrand': _rebrand
   -        }) | trim | indent(8) }}
   +        <img class="govuk-header__logotype ate-header__logotype" src="{{ url_for('static', filename='ate-header/ATE_WHITE_LANDSCP_AW.png') }}" alt="Active Travel England"/>
   +        <img class="govuk-header__logotype ate-header__logotype--focus" src="{{ url_for('static', filename='ate-header/ATE_BLK_LANDSCP_AW.png') }}" alt="Active Travel England"/>
   ```

### Upgrading Playwright package

After upgrading Playwright to a new minor version, reinstall the browsers and their dependencies:

```bash
playwright install --with-deps chromium
```

## Upgrading Node

To upgrade Node:

1. Update Node to the [latest LTS version](https://nodejs.org/en/download) in [package.json](../package.json):

   ```json
   "engines": {
     "node": "<version>",
     ...
   }
   ```

1. Align npm to the [version supplied with Node](https://nodejs.org/en/about/previous-releases) in [package.json](../package.json):

   ```json
   "engines": {
     ...
     "npm": "<version>"
   }
   ```

1. Update the [lock file](../package-lock.json):

   ```bash
   npm install --package-lock-only
   ```

1. Update the Node version in the [CI workflow](../.github/workflows/ci.yml):

   ```yml
   - name: Setup Node
     uses: actions/setup-node@v4
     with:
       node-version: <version>
   ```

1. Update the Node version in the [README](../README.md) prerequisites

## Upgrading Node packages

To list Node packages that need upgrading:

```bash
npm outdated
```

To upgrade packages to their latest patch versions:

```bash
npm upgrade
```

### Upgrading GOV.UK One Login Service Header package

This dependency uses a [GitHub URL](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#github-urls) as it
doesn't publish a Node package. To upgrade:

1. Update the commit hash for the dependency `govuk-one-login-service-header` in [package.json](../package.json) to the
   [latest release](https://github.com/govuk-one-login/service-header/releases)'s commit (tags don't seem reliable with
   GitHub URLs)

1. Install the updated package:

   ```bash
   npm install
   ```

1. The package [doesn't provide Jinja templates](https://github.com/govuk-one-login/service-header/issues/25), so copy
   the contents of the installed package's [service header Nunjucks template](../node_modules/govuk-one-login-service-header/dist/nunjucks/di-govuk-one-login-service-header/template.njk)
   to [schemes/views/templates/ate_service_header/macro.html](../schemes/views/templates/ate_service_header/macro.html)
   replacing the contents of the Jinja macro:

   ```
   {% macro ateServiceHeader(params) %}

   <PASTE HERE>

   {% endmacro %}
   ```

   And update the service navigation component for Jinja by applying the following patches:

   ```diff
   -{%- from "node_modules/govuk-frontend/dist/govuk/components/service-navigation/macro.njk" import govukServiceNavigation -%}
   +{%- from "govuk_frontend_jinja/components/service-navigation/macro.html" import govukServiceNavigation -%}
   ```
   
   ```diff
   -      {{ govukServiceNavigation({
   -        menuButtonText: params.menuButtonText,
   -        menuButtonLabel: params.menuButtonLabel,
   -        serviceName: params.serviceName,
   -        navigation: navArr
   -      }) if params.serviceName }}
   +      {{ govukServiceNavigation({
   +        "menuButtonText": params.menuButtonText,
   +        "menuButtonLabel": params.menuButtonLabel,
   +        "serviceName": params.serviceName,
   +        "navigation": navArr
   +      }) if params.serviceName }}
   ```

1. The template [doesn't allow the crown logo to be customised](https://github.com/govuk-one-login/service-header/issues/40),
   so replace it with the ATE logo by applying the following patch:

   ```diff
          <div class="one-login-header__logo">
            <a href="{{ homepageLink }}" class="one-login-header__link one-login-header__link--homepage">
   -          <svg
   -            focusable="false"
   -            role="img"
   -            class="one-login-header__logotype"
   -            xmlns="http://www.w3.org/2000/svg"
   -            viewBox="0 0 148 30"
   -            height="30"
   -            width="148"
   -            aria-label="GOV.UK">
   -            <title>GOV.UK</title>
   -            <path d="M22.6 10.4c-1 .4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s-.1 2-1 2.4m-5.9 6.7c-.9.4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s-.1 2-1 2.4m10.8-3.7c-1 .4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s0 2-1 2.4m3.3 4.8c-1 .4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s-.1 2-1 2.4M17 4.7l2.3 1.2V2.5l-2.3.7-.2-.2.9-3h-3.4l.9 3-.2.2c-.1.1-2.3-.7-2.3-.7v3.4L15 4.7c.1.1.1.2.2.2l-1.3 4c-.1.2-.1.4-.1.6 0 1.1.8 2 1.9 2.2h.7c1-.2 1.9-1.1 1.9-2.1 0-.2 0-.4-.1-.6l-1.3-4c-.1-.2 0-.2.1-.3m-7.6 5.7c.9.4 2-.1 2.4-1 .4-.9-.1-2-1-2.4-.9-.4-2 .1-2.4 1s0 2 1 2.4m-5 3c.9.4 2-.1 2.4-1 .4-.9-.1-2-1-2.4-.9-.4-2 .1-2.4 1s.1 2 1 2.4m-3.2 4.8c.9.4 2-.1 2.4-1 .4-.9-.1-2-1-2.4-.9-.4-2 .1-2.4 1s0 2 1 2.4m14.8 11c4.4 0 8.6.3 12.3.8 1.1-4.5 2.4-7 3.7-8.8l-2.5-.9c.2 1.3.3 1.9 0 2.7-.4-.4-.8-1.1-1.1-2.3l-1.2 4c.7-.5 1.3-.8 2-.9-1.1 2.5-2.6 3.1-3.5 3-1.1-.2-1.7-1.2-1.5-2.1.3-1.2 1.5-1.5 2.1-.1 1.1-2.3-.8-3-2-2.3 1.9-1.9 2.1-3.5.6-5.6-2.1 1.6-2.1 3.2-1.2 5.5-1.2-1.4-3.2-.6-2.5 1.6.9-1.4 2.1-.5 1.9.8-.2 1.1-1.7 2.1-3.5 1.9-2.7-.2-2.9-2.1-2.9-3.6.7-.1 1.9.5 2.9 1.9l.4-4.3c-1.1 1.1-2.1 1.4-3.2 1.4.4-1.2 2.1-3 2.1-3h-5.4s1.7 1.9 2.1 3c-1.1 0-2.1-.2-3.2-1.4l.4 4.3c1-1.4 2.2-2 2.9-1.9-.1 1.5-.2 3.4-2.9 3.6-1.9.2-3.4-.8-3.5-1.9-.2-1.3 1-2.2 1.9-.8.7-2.3-1.2-3-2.5-1.6.9-2.2.9-3.9-1.2-5.5-1.5 2-1.3 3.7.6 5.6-1.2-.7-3.1 0-2 2.3.6-1.4 1.8-1.1 2.1.1.2.9-.3 1.9-1.5 2.1-.9.2-2.4-.5-3.5-3 .6 0 1.2.3 2 .9l-1.2-4c-.3 1.1-.7 1.9-1.1 2.3-.3-.8-.2-1.4 0-2.7l-2.9.9C1.3 23 2.6 25.5 3.7 30c3.7-.5 7.9-.8 12.3-.8m28.3-11.6c0 .9.1 1.7.3 2.5.2.8.6 1.5 1 2.2.5.6 1 1.1 1.7 1.5.7.4 1.5.6 2.5.6.9 0 1.7-.1 2.3-.4s1.1-.7 1.5-1.1c.4-.4.6-.9.8-1.5.1-.5.2-1 .2-1.5v-.2h-5.3v-3.2h9.4V28H55v-2.5c-.3.4-.6.8-1 1.1-.4.3-.8.6-1.3.9-.5.2-1 .4-1.6.6s-1.2.2-1.8.2c-1.5 0-2.9-.3-4-.8-1.2-.6-2.2-1.3-3-2.3-.8-1-1.4-2.1-1.8-3.4-.3-1.4-.5-2.8-.5-4.3s.2-2.9.7-4.2c.5-1.3 1.1-2.4 2-3.4.9-1 1.9-1.7 3.1-2.3 1.2-.6 2.6-.8 4.1-.8 1 0 1.9.1 2.8.3.9.2 1.7.6 2.4 1s1.4.9 1.9 1.5c.6.6 1 1.3 1.4 2l-3.7 2.1c-.2-.4-.5-.9-.8-1.2-.3-.4-.6-.7-1-1-.4-.3-.8-.5-1.3-.7-.5-.2-1.1-.2-1.7-.2-1 0-1.8.2-2.5.6-.7.4-1.3.9-1.7 1.5-.5.6-.8 1.4-1 2.2-.3.8-.4 1.9-.4 2.7zM71.5 6.8c1.5 0 2.9.3 4.2.8 1.2.6 2.3 1.3 3.1 2.3.9 1 1.5 2.1 2 3.4s.7 2.7.7 4.2-.2 2.9-.7 4.2c-.4 1.3-1.1 2.4-2 3.4-.9 1-1.9 1.7-3.1 2.3-1.2.6-2.6.8-4.2.8s-2.9-.3-4.2-.8c-1.2-.6-2.3-1.3-3.1-2.3-.9-1-1.5-2.1-2-3.4-.4-1.3-.7-2.7-.7-4.2s.2-2.9.7-4.2c.4-1.3 1.1-2.4 2-3.4.9-1 1.9-1.7 3.1-2.3 1.2-.5 2.6-.8 4.2-.8zm0 17.6c.9 0 1.7-.2 2.4-.5s1.3-.8 1.7-1.4c.5-.6.8-1.3 1.1-2.2.2-.8.4-1.7.4-2.7v-.1c0-1-.1-1.9-.4-2.7-.2-.8-.6-1.6-1.1-2.2-.5-.6-1.1-1.1-1.7-1.4-.7-.3-1.5-.5-2.4-.5s-1.7.2-2.4.5-1.3.8-1.7 1.4c-.5.6-.8 1.3-1.1 2.2-.2.8-.4 1.7-.4 2.7v.1c0 1 .1 1.9.4 2.7.2.8.6 1.6 1.1 2.2.5.6 1.1 1.1 1.7 1.4.6.3 1.4.5 2.4.5zM88.9 28 83 7h4.7l4 15.7h.1l4-15.7h4.7l-5.9 21h-5.7zm28.8-3.6c.6 0 1.2-.1 1.7-.3.5-.2 1-.4 1.4-.8.4-.4.7-.8.9-1.4.2-.6.3-1.2.3-2v-13h4.1v13.6c0 1.2-.2 2.2-.6 3.1s-1 1.7-1.8 2.4c-.7.7-1.6 1.2-2.7 1.5-1 .4-2.2.5-3.4.5-1.2 0-2.4-.2-3.4-.5-1-.4-1.9-.9-2.7-1.5-.8-.7-1.3-1.5-1.8-2.4-.4-.9-.6-2-.6-3.1V6.9h4.2v13c0 .8.1 1.4.3 2 .2.6.5 1 .9 1.4.4.4.8.6 1.4.8.6.2 1.1.3 1.8.3zm13-17.4h4.2v9.1l7.4-9.1h5.2l-7.2 8.4L148 28h-4.9l-5.5-9.4-2.7 3V28h-4.2V7zm-27.6 16.1c-1.5 0-2.7 1.2-2.7 2.7s1.2 2.7 2.7 2.7 2.7-1.2 2.7-2.7-1.2-2.7-2.7-2.7z"></path>
   -          </svg>
   +          <img class="one-login-header__logotype ate-header__logotype" src="{{ url_for('static', filename='ate-header/ATE_WHITE_LANDSCP_AW.png') }}" alt="Active Travel England"/>
   +          <img class="one-login-header__logotype ate-header__logotype--focus" src="{{ url_for('static', filename='ate-header/ATE_BLK_LANDSCP_AW.png') }}" alt="Active Travel England"/>
            </a>
          </div>
   ```

## Upgrading Terraform

To upgrade Terraform the [latest minor version](https://developer.hashicorp.com/terraform/install#release-information):

1. For each Terraform root module in [cloud](../cloud), update the required version in `versions.tf` keeping the patch version zero:

   ```hcl
   terraform {
     required_version = "~> <version>"
     ...
   }
   ```

1. Update the Terraform version in the [CI workflow](.github/workflows/ci.yml):

   ```yaml
   - name: Setup Terraform
     uses: hashicorp/setup-terraform@v3
     with:
       terraform_version: '~<version>'
   ```

1. Update the Terraform version in the [README](../README.md) prerequisites

## Upgrading Terraform providers

To upgrade each Terraform root module in [cloud](../cloud):

1. Update the providers in `versions.tf` to the latest minor or major version keeping the patch version zero,
   e.g. `~> 1.2.0` to `~> 1.3.0`

1. Install the upgraded providers:

   ```bash
   terraform init -upgrade
   ```

## Upgrading GitHub Actions

To upgrade all workflows in [.github/workflows](../.github/workflows):

1. Update each action to its latest major version, e.g. for `actions/setup-python` see [actions/setup-python](https://github.com/actions/setup-python/releases)

1. Update [runner images](https://github.com/actions/runner-images) to their latest version

## Upgrading Cloud SQL Auth Proxy

To upgrade [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy) to the
[latest version](https://github.com/GoogleCloudPlatform/cloud-sql-proxy/releases):

1. Update the version in the [cloud-run](../cloud/schemes/cloud-run/main.tf) Terraform module:

   ```hcl
   containers {
     image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:<version>"
     ...
   }
   ```

1. Update the version in the [proxy.sh](../proxy.sh) script:

   ```bash
   docker run --rm \
       ...
       gcr.io/cloud-sql-connectors/cloud-sql-proxy:<version> \
       ...
   ```
