TEST_IMAGE = rpm-shim-tests
BASE_IMAGE ?=
INSTALL_DEPS_CMD ?=

CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)

test-image:
	$(CONTAINER_ENGINE) build --rm \
		--tag $(TEST_IMAGE) \
		-f tests/Containerfile \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		--build-arg INSTALL_DEPS_CMD="$(INSTALL_DEPS_CMD)" \
		.

test: test-image
	$(CONTAINER_ENGINE) run --rm -ti $(TEST_IMAGE)
