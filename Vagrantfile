# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.3.0"

# Environmental Variables:
ENV['HOSTNAME'] = "vagrant.test"
ENV['VERBOSITY'] = 'v'

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Configure the VirtualBox guest host:
  config.vm.define ENV['HOSTNAME'] do |node|

    # Specify the Vagrant Box, version, and update check:
    node.vm.box = "geerlingguy/centos7"
    node.vm.box_version = "1.2.27"
    node.vm.box_check_update = "false"

    # Disable the default mount:
    node.vm.synced_folder '.', '/vagrant', disabled: true

    # Customize the hostname:
    node.vm.hostname = ENV['HOSTNAME']

    # Forward the ports:
    node.vm.network "forwarded_port", guest: 8080, host: 8080
    node.vm.network "forwarded_port", guest: 5901, host: 5901

    # VirtualBox Provider
    node.vm.provider "virtualbox" do |vb|
      # Customize the number of CPUs on the VM:
      vb.cpus = 3

      # Customize the amount of memory on the VM:
      vb.memory = 10000

      # Customize the name that appears in the VirtualBox GUI:
      vb.name = ENV['HOSTNAME']
    end

    # Provision with shell scripts.
    node.vm.provision "shell", inline: <<-SHELL
    sysctl user.max_user_namespaces=15000
    yum install -y git podman
    ln -s /usr/bin/podman /usr/bin/docker
    useradd -m podman
    usermod --add-subuids 200000-201000 --add-subgids 200000-201000 podman
    loginctl enable-linger podman
    mkdir -p /scratch/local/podman/
    chown -R podman:podman /scratch/local/podman/
    SHELL

  end

end