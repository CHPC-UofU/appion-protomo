# Makefile

# Silence any make output to avoid interfere with manifests apply.
MAKEFLAGS += -s

# General variables:
CONTAINER_FILE = Dockerfile
KUBE_FILE = pod.yml
PODMAN_POD_NAME = appionprotomo
PODMAN_CONTAINER_NAME = appionprotomo
SERVICE_NAME := $$(systemd-escape $(CURDIR)/$(KUBE_FILE))

# ---------------------------------------------------------
# Common targets
# ---------------------------------------------------------

default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -/]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ---------------------------------------------------------
# Systemd targets
# ---------------------------------------------------------

.PHONY: systemd/disable
systemd/disable: # Disable the associated systemd service.
	@echo ">>> Disabling 'podman-kube@$(SERVICE_NAME).service'"
	systemctl --user disable "podman-kube@$(SERVICE_NAME).service"

.PHONY: systemd/enable
systemd/enable: # Enable the associated systemd service.
	@echo ">>> Enabling 'podman-kube@$(SERVICE_NAME).service'"
	systemctl --user enable "podman-kube@$(SERVICE_NAME).service"

.PHONY: systemd/start
systemd/start: # Start the associated systemd service.
	@echo ">>> Starting 'podman-kube@$(SERVICE_NAME).service'"
	systemctl --user start "podman-kube@$(SERVICE_NAME).service"
	sleep 1
	systemctl --user status --no-pager "podman-kube@$(SERVICE_NAME).service"

.PHONY: systemd/status
systemd/status: # View the status of the associated systemd service.
	@echo ">>> Displaying status for 'podman-kube@$(SERVICE_NAME).service'"
	systemctl --user status --no-pager "podman-kube@$(SERVICE_NAME).service"

.PHONY: systemd/stop
systemd/stop: # Stop the associated systemd service.
	@echo ">>> Stopping 'podman-kube@$(SERVICE_NAME).service'"
	systemctl --user stop "podman-kube@$(SERVICE_NAME).service"
	sleep 1
	systemctl --user status --no-pager "podman-kube@$(SERVICE_NAME).service" || exit 0

# ---------------------------------------------------------
# Podman targets
# ---------------------------------------------------------
.PHONY: podman/build
podman/build: # Build a local image (use GitLab's build process in production).
	@echo ">>> Build a local image"
	podman build --file $(CONTAINER_FILE) --tag localhost/$(PODMAN_CONTAINER_NAME):local .

.PHONY: podman/login
podman/login: # Log into the container.
	@echo ">>> Logging into the '$(PODMAN_POD_NAME)-$(PODMAN_CONTAINER_NAME)' container"
	podman exec -it $(PODMAN_POD_NAME)-$(PODMAN_CONTAINER_NAME) /bin/bash || (echo "> SUGGESTION: Check that 'podman-kube@$(SERVICE_NAME).service' is running."; exit 1)

.PHONY: podman/volumerm
podman/volumerm: # Remove all associated podman volumes.
	@echo ">>> Removing associated podman volumes."
	podman volume ls
	podman volume rm mariadb-database || exit 0
	podman volume ls