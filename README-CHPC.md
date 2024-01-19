# Appion-Protomo

This document is specific to CHPC maintenance workflows (see the [README](README.md) for full details on the software stack).

## Overview

* This repository is a fork of https://github.com/nysbc/appion-protomo and incorporates local changes made by [Martin Cuma](mailto:mcuma@utah.edu).
* Aiding us in authoring and storing a new image is a light-weight automation pipeline described in `.gitlab-ci.yml`.

## Creating a new container image

1. Use the `Vagrantfile` to spin up a Rocky 8.8 host for mounting and testing changes in a controlled environment using the `make dev/XXXX` targets.
   * If you prefer not to use Vagrant, replicate the required pre-requisite commands described in the `Vagrantfile` provisioning shell expression for your dev user on your dev host and modify `kube.dev.yml` accordingly.
2. **Optional:** Any commits on a feature branch linked to a merge request will trigger a `podman build ...` command. This can be thought of testing the source, i.e. can it even build before I go about trying to deploy?
3. Any git tag created and resembling a semantic version string will trigger a container image build and deployment to the [GitLab repository's container registry](https://gitlab.chpc.utah.edu/chpc/projects/appion-protomo/container_registry). For example, a new git tag resembling `x.y.z` will result in the image tag `gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:x.y.z`.

### Required manual source edits

1. Before creating a new git tag, remember to commit an update to `kube.prod.yml` referencing the upcoming tag (and optionally update this README as well).

   In the example below, the tag would be `2.1.1`.

   **Example: kube.prod.yml**
   ```yaml
   ...
   - name: appionprotomo
     image: 'gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:2.1.1'
   ...
   ```

## Running the pod w/systemd

> **_NOTE:_** We have moved the `/emg/data` directory outside the repository to prevent its persistent data from being accidentally deleted during the various `git` commands described below.

1. Ensure lingering is enabled for the user account that will be running the `podman` container images.

   ```shell
   [unid@localhost:~]
   $ loginctl enable-linger <podmanuser>
   ```

1. Switch to the local user who will be executing the `podman` commands and set the necessary environmental variables.

   ```shell
   [unid@localhost:~]
   $ sudo su - <podmanuser>
   ...
   [podmanuser@localhost:~] 
   $ export XDG_RUNTIME_DIR=/run/user/$(id -ru)
   ```

1. Log into the GitLab container registry using your uNID.

   ```shell
   [podmanuser@localhost:~] 
   $ podman login --username <uNID> gitlab.chpc.utah.edu:5050
   Password: 
   WARNING! Your password will be stored unencrypted in ...
   ...
   
   Login Succeeded
   ```

1. Pull the tagged container image (e.g. `2.1.1`) from GitLab's container registry.

   ```shell
   [podmanuser@localhost:~] 
   $ podman pull gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:2.1.1
   0.0.1: Pulling from chpc/projects/appion-protomo
   Digest: sha256:9f91318a812dc84719b7a07aa3b6d944103fd9d56286cdc40d74fef58816c469
   Status: Image is up to date for gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:2.1.1
   gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:2.1.1
   ```

1. Log out of the GitLab container registry on the host to remove the unencrypted credentials file.

   ```shell
   [podmanuser@localhost:~] 
   $ podman logout gitlab.chpc.utah.edu:5050
   Removing login credentials for ...
   ```

1. If an existing repository clone already exists on the host, remove it.

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ rm -rf appion-protomo
   ```

1. In a directory on the host, clone the tagged source from GitLab. For example:

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ git clone --depth 1 --branch 2.1.1 https://gitlab.chpc.utah.edu/chpc/projects/appion-protomo.git
   ...
   ...
   Note: switching to 'f7848ae9a81206a2999a4042d641021a48c8fded'.
   
   You are in 'detached HEAD' state.
   ...
   [podmanuser@localhost:/path/to/location]
   $ cd appion-protomo
   ```

1. **(Optional)** Locally modify the absolute `.spec.volumes[*].hostPath.path`s in `kube.prod.yml` to point to appropriate locations on the host.

   **Example: Old**
   ```yaml
   volumes:
     - name: emg-data
       hostPath:
         path: /scratch/local/podman/emg/data                      <------------------------
         type: Directory
     ...
   ```

   **Example: New**
   ```yaml
   volumes:
     - name: emg-data
       hostPath:
         path: /path/to/emg/data                                   <------------------------
         type: Directory
     ...
   ```

1. Create the persistent data directory if it does not already exist.

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ mdkir -p emg/data
   ```

1. Start and enable the systemd service to survive host reboot.

   ```shell
   [podmanuser@localhost:/path/to/location/appion-protomo]
   $ make systemd/start
   ...
   $ make systemd/enable
   ...
   ```

For other available recipes see:

```shell
[podmanuser@localhost:/path/to/location/appion-protomo]
$ make help
...
```

### Additional Resources

* [How to run Kubernetes workloads in systemd with Podman](https://www.redhat.com/sysadmin/kubernetes-workloads-podman-systemd)
* [Configure a container to start automatically as a systemd service](https://www.redhat.com/sysadmin/container-systemd-persist-reboot)
* [podman kube play](https://docs.podman.io/en/stable/markdown/podman-kube-play.1.html)
