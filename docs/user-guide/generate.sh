#!/bin/bash

docker run --rm \
	-v "$(pwd)":/data \
	-u "$(id -u):$(id -g)" \
	pandoc/extra \
	--output=index.pdf \
	index.md
