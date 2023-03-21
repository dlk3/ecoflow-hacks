# My EcoFlow Delta Pro Hacks

### Log selected Delta Pro metrics into a MariaDB database and control AC vs solar battery charging

* **ecoflow-logging** Python script that uses:
* * **ecoflow.py** EcoFlow API module adapted from the [vwt12eh8/hassio-ecoflow GitHub project](https://github.com/vwt12eh8/hassio-ecoflow)
* * **smartthings.py** SmartThings API module
* * **ecoflow-logger.timer** Systemd timer that triggers ecoflow-logger.service once a minute
* * **ecoflow-logger.service** Systemd service file that executes the ecoclow-logger script

The ecoflow.py API module uses the reactivex module which is not available in the Fedora repositories I use.  I use the following commands to create a virtual Python environment in which to run this script:
<pre>cd /opt/ecoflow 
python -m venv ecoflow-python
/opt/ecoflow/ecoflow-python/bin/pip install reactivex requests PyMySQL mysqlclient</pre>

The logger script can now be run with this command:
<pre>/opt/ecoflow/ecoflow-python/bin/python /opt/ecoflow/ecoflow-logger</pre>

### Show the status of the Delta Pro on a Nagios dashboard 

A Nagios plugin for the Delta Pro that queries the MariaDB database for status:

* **check_ecoflow** Python script
 
### Grafana dashboard using metrics from the MariaDB database

* **grafana.json**


