|travis-badge|_

.. |travis-badge| image:: https://travis-ci.com/IBM/Musketeer-Client.svg?branch=master
.. _travis-badge: https://travis-ci.com/IBM/Musketeer-Client/

========================
Musketeer Client-Package
========================

The contents of this repository describe how to interact with the IBM Musketeer cloud platform for federated machine learning. It is primarily targeted at algorithm developers who are planning to design and run federated machine learning algorithms.

Prerequisites
---------------------------------

It is assumed that all development takes place in Python, using at least version 3.6.

To speed up the creation of a development environment and generally for ease of use, the provisioning of a virtual machine is automated and appropriate dependencies are installed during this process. To take advantage of this, you must have vagrant installed on your system (and backed by a hypervisor such as VirtualBox).

For Mac users, using HomeBrew:

.. code-block::

        brew cask install virtualbox
        brew cask install vagrant
        vagrant plugin install vagrant-vbguest

Or for Windows:

.. code-block::

        Install VirtualBox - https://www.virtualbox.org/wiki/Downloads
        Install Vagrant - https://www.vagrantup.com/downloads.html
        vagrant plugin install vagrant-vbguest

If you choose not to bring up a VM, please see the Vagrantfile_ for dependencies to manually install.

.. _Vagrantfile: Vagrantfile 

**Note:** Musketeer platform **credentials** and the server **certificate** must be available. Please request these from the IBM team.


Virtual Machine Interactions
---------------------------------

This VM provides terminal capabilities only, and the current directory will be shared between the host and the VM.

- To create the VM, from the terminal, change directory to the root directory of this repository and run:

.. code-block::

	vagrant up

- This will take a few minutes. Upon completion, run:

.. code-block::

        vagrant ssh

to log into the newly created VM.

- To stop the VM:

.. code-block::

        vagrant halt

- And if you are finished with the VM:

.. code-block::

        vagrant destroy


Tests
---------------------------------

There is a test provided which will verify access to the platform based on the available credentials.

.. code-block::

	python3 -m pytest tests/basic.py --credentials=CREDENTIALS FILE -srx -s


Demo
---------------------------------

The demo is located in the ``demo`` directory, and can be run by:

- Creating a user to represent the aggregator
- Creating one or more users to represent task participants
- Creating a task
- Starting the aggregator
- Listing the available tasks
- Joining a task
- Starting one or more workers

.. code-block::

	python3 register.py --credentials <credentials.json> --user <AGGREGATOR USER> --password <> --org <>
	python3 register.py --credentials <credentials.json> --user <WORKER USER> --password <> --org <>
	python3 creator.py --credentials <credentials.json> --user <AGGREGATOR USER> --password <> --task_name <>
	python3 aggregator.py --credentials <credentials.json> --user <AGGREGATOR USER> --password <> --task_name <>
	python3 listing.py --credentials <credentials.json>
	python3 join.py --credentials <credentials.json> --user <WORKER USER> --password <> --task_name <>
	python3 participant.py --credentials <credentials.json> --user <WORKER USER> --password <> --task_name <>


Notebook Demo
---------------------------------

Within the VM terminal, run:

.. code-block::

	jupyter notebook password
	jupyter notebook --ip=0.0.0.0 &


Open ``127.0.0.1:8881`` in your host browser (Chrome or Firefox), enter the password you chose and then you should see the navigation tree.

Run the ``task_creator.ipnyb`` notebook for the workflow of a task creator / aggregator.

Run the ``task_participant.ipnyb`` notebook for the workflow of a task participant.


Local Mode
---------------------------------
To facilitate research, we support a local version of the Musketeer platform, which is developed on flask. This local version has an assumption that there is only one task running at a time. In order to run tasks locally, run the following command:

.. code-block::

    python3 local_platform/musketeer.py

Note that, it is easy to switch between `local` and `cloud` platforms by changing the `config` file as follows: `{"platform": "local"}` for local platform and `{"platform": "cloud"}` for cloud platform.
