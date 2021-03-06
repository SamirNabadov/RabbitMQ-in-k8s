__RabbitMQ in Kubernetes Environment__
======================================

RabbiMQ installation and configuration based Python script in Kubernetes environment


__Configured software__
------------
* RabbitMQ 3.8.21


__Basic settings__
------------
* Deployed RabbitMQ based StatefulSet
* Implementation of Ingress
* Created vhost and users, configured permissions
* Configured HA policy

__Note__
------------
* In the daemonset of Nginx Ingress settings should have this argument: - --tcp-services-configmap=$(POD_NAMESPACE)/tcp-services
* In the service of Nginx Ingress must be exposed required tcp socket (AMPQ 5672)

__Requirements__
------------
* Python 3.8.10
* Kubectl client
* Kubernetes Cluster Environment

Running the Deployment
----------------------

__To deploy__

`$ python3 setup.py`

__Author Information__
------------------

Samir Nabadov
