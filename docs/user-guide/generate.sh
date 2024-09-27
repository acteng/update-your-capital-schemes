#!/bin/bash

docker run --rm \
	-v "$(pwd)":/data \
	-u "$(id -u):$(id -g)" \
	pandoc/latex \
	-H disable-float.tex \
	--output=index.pdf \
	index.md
