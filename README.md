# EASE-MAPE-System

We want to develop a MAPE framework. Being a framework, we want the components of (M)onitoring, (A)nalysis, (P)lanning, (E)xecution need to be extendable to allow for plugging services from external providers. More specifically, the framework components need to be abstract and simply define an interface to access the functionality of the individual component. Assuming that this functionality is provided by most corresponding services by cloud or infrastructure providers, the implementation of these interfaces will call the external services and be called by other classes of the framework. The target platforms may include Amazon EC2, OpenStack, Docker and Kubernetes (with the last two being a first priority).

Python version : 3.6

**User manual :**
https://docs.google.com/document/d/1reJniVGFsFay0vmqaKLxVgArONzC0NXDCdRdKX7rKW0/edit?usp=sharing

### **Requirements**

See [requirements.txt](./requirements.txt) 


### **Get started**
How to run :

* Monitoring only : [monitoring.sh](./monitoring.sh)

* Auto-scale : [autoscale.sh](./autoscale.sh)

* Local MongoDB database : [db.sh](./db.sh)

