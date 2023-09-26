black:
	.venv/bin/black schemes tests

isort:
	.venv/bin/isort schemes tests

terraform-fmt:
	terraform -chdir=cloud fmt -recursive

format: black isort terraform-fmt

mypy:
	.venv/bin/mypy schemes tests

pylint:
	.venv/bin/pylint schemes tests

lint: mypy pylint

test:
	.venv/bin/pytest

verify: lint test
