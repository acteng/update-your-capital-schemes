# Releasing

## Create a release

1. Ensure all GitHub issues are closed for the milestone
1. Close the GitHub milestone for the release
1. Tag the repository for the release:
   ```bash
   git tag <version>
   ```
1. Push the tag:
   ```bash
   git push --tags
   ```
1. Wait for the [CI](https://github.com/acteng/update-your-capital-schemes/actions/workflows/ci.yml) GitHub Action to build and deploy the release to Dev
1. Confirm that Dev is working as expected
1. Publish a new GitHub release:
   * Tag: `<version>`
   * Title: `<version>`
   * Description: `Completed stories: <link to milestone closed issues>` 

## Deploy to Test

1. Apply Terraform infrastructure changes to Test:
   ```bash
   cd cloud/schemes
   terraform workspace select test
   terraform apply
   ```
1. Run the [Deploy](https://github.com/acteng/update-your-capital-schemes/actions/workflows/deploy.yml) GitHub Action to deploy the release to Test:
   * Environment: `Test`
   * Docker image tag: `<version>`
1. Confirm that Test is working as expected

## Deploy to Prod

1. Apply Terraform infrastructure changes to Prod:
   ```bash
   cd cloud/schemes
   terraform workspace select prod
   terraform apply
   ```
1. Run the [Deploy](https://github.com/acteng/update-your-capital-schemes/actions/workflows/deploy.yml) GitHub Action to deploy the release to Prod:
   * Environment: `Prod`
   * Docker image tag: `<version>`
1. Confirm that Prod is working as expected
