bin = .venv/bin
packages = schemes tests

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
