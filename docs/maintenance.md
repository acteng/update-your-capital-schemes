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

### Upgrading Playwright package

After upgrading Playwright to a new minor version, reinstall the browsers and their dependencies:

```bash
playwright install --with-deps chromium
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

### Upgrading GOV.UK One Login Service Header package

This dependency uses a [GitHub URL](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#github-urls) as
[it hasn't been released yet](https://github.com/govuk-one-login/service-header/issues/46). To upgrade:

1. Update the commit hash for the dependency `govuk-one-login-service-header` in `package.json` to the
   [latest commit](https://github.com/govuk-one-login/service-header/commits/main/)

1. Install the updated package:

   ```bash
   npm install
   ```

1. Copy the contents of
   [the service header Nunjucks template](https://raw.githubusercontent.com/govuk-one-login/service-header/main/src/nunjucks/template.njk)
   to `schemes/views/templates/ate_service_header/macro.html`, replacing the contents of the Jinja macro:

   ```
   {% macro ateServiceHeader(params) %}

   <PASTE HERE>

   {% endmacro %}
   ```

1. Apply the following diff to workaround https://github.com/govuk-one-login/service-header/issues/40:

   ```diff
          <div class="one-login-header__logo">
            <a href="{{ homepageLink }}" class="one-login-header__link one-login-header__link--homepage">
   -          <span class="one-login-header__logotype">
   -            <!--[if gt IE 8]><!-->
   -              <svg
   -                aria-hidden="true"
   -                focusable="false"
   -                class="one-login-header__logotype-crown"
   -                xmlns="http://www.w3.org/2000/svg"
   -                viewBox="0 0 32 30"
   -                height="30"
   -                width="32">
   -                <path fill="currentColor" fill-rule="evenodd" d="M22.6 10.4c-1 .4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s-.1 2-1 2.4m-5.9 6.7c-.9.4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s-.1 2-1 2.4m10.8-3.7c-1 .4-2-.1-2.4-1-.4-.9.1-2 1-2.4.9-.4 2 .1 2.4 1s0 2-1 2.4m3.3 4.
   -            </svg>
   -            <!--<![endif]-->
   -            <span>
   -              GOV.UK
   -            </span>
   -          </span>
   +          <img class="one-login-header__logotype ate-header__logotype" src="{{ url_for('static', filename='ate-header/ATE_WHITE_LANDSCP_AW.png') }}" alt="Active Travel England"/>
   +          <img class="one-login-header__logotype ate-header__logotype--focus" src="{{ url_for('static', filename='ate-header/ATE_BLK_LANDSCP_AW.png') }}" alt="Active Travel England"/>
            </a>
          </div>
   ```

## Upgrading Terraform providers

Upgrade each Terraform root module in `cloud`:

1. Upgrade the providers in `versions.tf` to the latest minor or major version keeping the patch version zero,
   e.g. `~> 1.2.0` to `~> 1.3.0`

1. Install the upgraded providers:

   ```bash
   terraform init -upgrade
   ```

## Upgrading GitHub Actions

Upgrade all workflows in `.github/workflows`:

1. Upgrade each action to its latest major version, e.g. for `actions/setup-python` see [actions/setup-python](https://github.com/actions/setup-python/releases)

1. Upgrade [runner images](https://github.com/actions/runner-images) to their latest version
