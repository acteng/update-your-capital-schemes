bin = .venv/bin
packages = schemes tests

clean:
	rm -rf .flask_session .mypy_cache .venv node_modules test-results
	rm -rf schemes/static/govuk-frontend schemes/static/govuk-one-login-service-header
	find . -name __pycache__ -type d -prune -exec rm -rf {} \;
	find . -name .pytest_cache -type d -prune -exec rm -rf {} \;

black-check:
	$(bin)/black --check $(packages)

isort-check:
	$(bin)/isort --check-only $(packages)

terraform-fmt-check:
	terraform -chdir=cloud fmt -check -recursive

format-check: black-check isort-check terraform-fmt-check

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

verify: format-check lint test

migrate:
	$(bin)/alembic upgrade head
	$(bin)/alembic revision --autogenerate -m "test"
	rm schemes.db
