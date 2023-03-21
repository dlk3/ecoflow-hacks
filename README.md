# My EcoFlow Delta Pro Hacks

### Log selected Delta Pro metrics into a MariaDB database and control AC vs solar battery charging

* **ecoflow-logging** Python script that uses:
* * **ecoflow.py** EcoFlow API module adapted from the [vwt12eh8/hassio-ecoflow GitHub project](https://github.com/vwt12eh8/hassio-ecoflow)
* * **smartthings.py** SmartThings API module

### Show the status of the Delta Pro on a Nagios dashboard (a Nagios plugin for the Delta Pro that queries the MariaDB database for status information)

* **check_ecoflow** Python script
 
### Grafana dashboard using metrics from the MariaDB database

* **grafana.json**


