# Appion-Protomo

This document is specific to CHPC maintenance workflows (see the [README](README.md) for full details on the software stack).

## Overview

* This repository is a fork of https://github.com/nysbc/appion-protomo and incorporates local changes made by [Martin Cuma](mailto:mcuma@utah.edu).
* Aiding us in authoring and storing a new image is a light-weight automation pipeline described in `.gitlab-ci.yml`.

## Creating a new container image

1. **Optional:** Any commits on a feature branch linked to a merge request will trigger a `podman build ...` command. This can be thought of testing the source, i.e. can it even build before I go about trying to deploy?
2. Any git tag created and resembling a semantic version string will trigger a container image build and deployment to the [GitLab repository's container registry](https://gitlab.chpc.utah.edu/chpc/projects/appion-protomo/container_registry). For example, a new git tag resembling `x.y.z` will result in the image tag `gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:x.y.z`.

### Required manual source edits

1. Before creating a new git tag, remember to commit an update to `run.sh` and `pod.yml` referencing the upcoming tag.

   In the examples below, the tag would be `1.2.3`.
   
   **Example: run.sh**
   ```shell
   ...
   APVERSION='1.2.3'
   ...
   ```
   
   **Example: pod.yml**
   ```yaml
   ...
   - name: appionprotomo
     image: 'gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3'
   ...
   ```

## Running the container image

There are several options for running the container image on a host with a modern Linux operating system. Each option and its associated steps are described below.
* For those with older host operating systems such as CentOS 7,  [The container method](#the-container-method) will be the only viable option due to older `podman` and `runc` packages.

### The container method

> **_NOTE:_** We have moved the `/emg/data` directory outside the repository to prevent its persistent data from being accidentally deleted during the various `git` commands described below. Override via the `$DATADIR` shell variable in `run.sh`.

1. On a host, either globally alias `docker` to `podman` or create a symbolic link to avoid having to translate the various shell scripts to the container engine of choice.

   ```shell
   [unid@localhost:/usr/bin]
   $ ls -al dock*
   lrwxrwxrwx. 1 root root 15 Dec  5  2022 docker -> /usr/bin/podman
   ```

2. Switch to the local user who will be executing the `podman` commands.

   ```shell
   [unid@localhost:~]
   $ sudo su - <podmanuser>
   ```

3. Log into the GitLab container registry using your uNID.

   ```shell
   [podmanuser@localhost:~] 
   $ podman login --username <uNID> gitlab.chpc.utah.edu:5050
   Password: 
   WARNING! Your password will be stored unencrypted in ...
   ...
   
   Login Succeeded
   ```

4. Pull the tagged container image (e.g. `1.2.3`) from GitLab's container registry.

   ```shell
   [podmanuser@localhost:~] 
   $ podman pull gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   0.0.1: Pulling from chpc/projects/appion-protomo
   Digest: sha256:9f91318a812dc84719b7a07aa3b6d944103fd9d56286cdc40d74fef58816c469
   Status: Image is up to date for gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   ```

5. Log out of the GitLab container registry on the host to remove the unencrypted credentials file.

   ```shell
   [podmanuser@localhost:~] 
   $ podman logout gitlab.chpc.utah.edu:5050
   Removing login credentials for ...
   ```

6. (If a previous container is running): Stop and remove it.

   ```shell
   [podmanuser@localhost:~] 
   $ podman container ls
   CONTAINER ID  IMAGE                                                         COMMAND               CREATED        STATUS        PORTS                                                                 NAMES
   12b24b238e83  gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3  /bin/sh -c /sw/st...  3 minutes ago  Up 3 minutes  0.0.0.0:3306->3306/tcp, 0.0.0.0:5901->5901/tcp, 0.0.0.0:8080->80/tcp  quizzical_torvalds
   ```
   
   Take the first three to four characters from the container ID and stop it. Podman may resort to a `SIGKILL` if necessary.
   
   ```shell
   [podmanuser@localhost:~] 
   $ podman container stop 12b
   WARN[0010] StopSignal SIGTERM failed to stop container quizzical_torvalds in 10 seconds, resorting to SIGKILL 
   12b
   ```
   
   Remove the stopped container.
   
   ```shell
   [podmanuser@localhost:~] 
   $ podman container rm 12b
   12b
   ```

   Finally, remove the old source directory on the host.

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ rm -rf ./appion-protomo
   ```

7. Clone the newly tagged source from GitLab. For example, if `1.2.3` was just created on GitLab:

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ git clone --depth 1 --branch 1.2.3 https://gitlab.chpc.utah.edu/chpc/projects/appion-protomo.git
   ...
   ...
   Note: switching to 'f7848ae9a81206a2999a4042d641021a48c8fded'.
   
   You are in 'detached HEAD' state.
   ...
   ```

8. Execute `run.sh`.

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ cd appion-protomo
   [podmanuser@localhost:/path/to/location/appion-protomo]
   $ ./run.sh 
   Using existing mariadb-database volume.
   Done.
   Creating data directory /path/to/location/appion-protomo/../emg/data if it does not already exist...
   12b24b238e83d609632ba71aad9e29ad3786788edea021fd7c3aec9783e08938
   Waiting for database...
   Done.
   ```

9. Finally, implement a method for managing the container as a lingering user (needs to be done only once).

   ```shell
   [unid@localhost:~]
   $ loginctl enable-linger <podmanuser>
   ```
   
   Examples include:

   * crontab
   * systemd user services (non-CentOS 7 hosts)

### The pod method w/systemd

1. Switch to the local user who will be executing the `podman` commands and set the necessary environmental variables.

   ```shell
   [unid@localhost:~]
   $ sudo su - <podmanuser>
   ...
   [podmanuser@localhost:~] 
   $ export XDG_RUNTIME_DIR=/run/user/$(id -ru)
   ```

2. Log into the GitLab container registry using your uNID.

   ```shell
   [podmanuser@localhost:~] 
   $ podman login --username <uNID> gitlab.chpc.utah.edu:5050
   Password: 
   WARNING! Your password will be stored unencrypted in ...
   ...
   
   Login Succeeded
   ```

3. Pull the tagged container image (e.g. `1.2.3`) from GitLab's container registry.

   ```shell
   [podmanuser@localhost:~] 
   $ podman pull gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   0.0.1: Pulling from chpc/projects/appion-protomo
   Digest: sha256:9f91318a812dc84719b7a07aa3b6d944103fd9d56286cdc40d74fef58816c469
   Status: Image is up to date for gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:1.2.3
   ```

4. Log out of the GitLab container registry on the host to remove the unencrypted credentials file.

   ```shell
   [podmanuser@localhost:~] 
   $ podman logout gitlab.chpc.utah.edu:5050
   Removing login credentials for ...
   ```

5. In a directory on the host, clone the tagged source from GitLab. For example:

   ```shell
   [podmanuser@localhost:/path/to/location]
   $ git clone --depth 1 --branch 1.2.3 https://gitlab.chpc.utah.edu/chpc/projects/appion-protomo.git
   ...
   ...
   Note: switching to 'f7848ae9a81206a2999a4042d641021a48c8fded'.
   
   You are in 'detached HEAD' state.
   ...
   [podmanuser@localhost:/path/to/location]
   $ cd appion-protomo
   ```

6. **(Optional)** Locally modify the absolute `.spec.volumes[*].hostPath.path`s in `pod.yml` to point to appropriate locations on the host.

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

7. Start and enable the SystemD service.

   ```shell
   [podmanuser@localhost:/path/to/location/appion-protomo]
   $ make systemd/start
   ...
   $ make systemd/enable
   ...
   ```

8. For other available recipes see:

   ```shell
   [podmanuser@localhost:/path/to/location/appion-protomo]
   $ make help
   ...
   ```

### Additional Resources

* [How to run Kubernetes workloads in systemd with Podman](https://www.redhat.com/sysadmin/kubernetes-workloads-podman-systemd)
