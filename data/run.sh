#!/bin/bash

docker run \
	--rm \
	--interactive \
	--tty \
	--volume ${PWD}:/workdir \
	--network=host \
	--env-file ../.env \
	jetbrains/intellij-http-client \
	$*
