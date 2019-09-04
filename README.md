# EASE-MAPE-System

We want to develop a MAPE framework. Being a framework, we want the components of (M)onitoring, (A)nalysis, (P)lanning, (E)xecution need to be extendable to allow for plugging services from external providers. More specifically, the framework components need to be abstract and simply define an interface to access the functionality of the individual component. Assuming that this functionality is provided by most corresponding services by cloud or infrastructure providers, the implementation of these interfaces will call the external services and be called by other classes of the framework. The target platforms may include Amazon EC2, OpenStack, Docker and Kubernetes (with the last two being a first priority).

**Monitoring algorithm**
Python version : 3.6

