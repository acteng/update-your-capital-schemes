bin = .venv/bin
packages = schemes tests

clean:
	rm -rf .flask_session .mypy_cache .venv node_modules
	rm -rf schemes/static/govuk-frontend schemes/static/govuk-one-login-service-header
	find . -name __pycache__ -type d -prune -exec rm -rf {} \;
	find . -name .pytest_cache -type d -prune -exec rm -rf {} \;

black:
	$(bin)/black $(packages)

isort:
	$(bin)/isort $(packages)

terraform-fmt:
	terraform -chdir=cloud fmt -recursive

format: black isort terraform-fmt

mypy:
	$(bin)/mypy $(packages)

pylint:
	$(bin)/pylint $(packages)

lint: mypy pylint

test:
	$(bin)/pytest

verify: lint test
