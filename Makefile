bin = .venv/bin

black:
	$(bin)/black schemes tests

isort:
	$(bin)/isort schemes tests

terraform-fmt:
	terraform -chdir=cloud fmt -recursive

format: black isort terraform-fmt

mypy:
	$(bin)/mypy schemes tests

pylint:
	$(bin)/pylint schemes tests

lint: mypy pylint

test:
	$(bin)/pytest

verify: lint test
