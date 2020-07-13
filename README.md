Sandhill
---------------

* [General Setup](#general-setup)
* [Local Setup](#local-setup)
* [Docker Setup](#docker-setup)
* [Routes](#routes)
* [Docker](#docker)

General Setup
===============

Make a copy of the default config and override any values you like. If not specified 
in a separate config file, the defaults will be used. This step is not required if you 
want to use the defaults for everything.

```
cp instance/sandhill.default_settings.cfg instance/sandhill.cfg
```

Install dependencies required for any setup.  
```
apt install python3-pip apache2
```

Local Setup
===============
Use this setup if you want to set up a development environment that allows 
code changes to be made and immediately updated on the page. 

### Install the required packages  
```
apt install virtualenv libapache2-mod-wsgi-py3 libapache2-mod-wsgi-py3
```

In the cloned directory, create the virtual environment.
```
virtualenv -p python3 env
```

Install the required Pip packages  
```
env/bin/pip install -r requirements.txt
```

## Create a log directory
```
mkdir -p /var/log/sandhill
```

## Setup logrotate on logs
TODO

## Create the rsyslog config
This step is required to have filtered logging for only this application go to 
a file other than syslog. This is only because `StandardOutput` and `StandardError` 
do not support file redirection in Ubuntu 16.04.

```
cp etc/rsyslog.d/sandhill.conf /etc/rsyslog.d/
chown -R syslog:adm /var/log/sandhill
```

### Create the service
Copy the systemd unit file to set it up as a service. 
```
cp etc/systemd/system/sandhill.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sandhill
systemctl start sandhill
```

### Setup Apache
Copy the apache site config and make required local changes to it.  
```
cp apache2/sandhill_local.conf /etc/apache2/sites-available/sandhill.conf
a2ensite sandhill.conf
systemctl restart apache2
```

Docker Setup
===============
Use this setup if you just want to set up a server to host the site without needing to make 
frequent changes to the code. 

### Install Docker
```
apt update
apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
```

When adding the key and source to apt:  
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

Finally, update apt sources and install Docker and supporting packages:  
```
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io docker-compose
```

## Install Docker Compose
```
sudo pip3 install docker-compose
```

### Build the Image
Build a new image based on the current code. TODO -- this will change once we have CI/CD, since we will 
not be building the image on each server.
```
docker-compose build
```

### Run the Image
Run the image in a detached mode. TODO -- we will have this be a service we set up on the server. 
```
docker-compose up -d
```

Note: If you need to manually take it down, run `docker-compose down`. TODO -- this will be moved to a service. 

To view logs of a given container just run:
```
docker contrainer ls
docker logs -f <CONTAINER NAME>
```

### Setup Apache
Copy the apache site config and make required local changes to it.  
```
cp apache2/sandhill_docker.conf /etc/apache2/sites-available/sandhill.conf
a2ensite sandhill.conf
systemctl restart apache2
```

### CI/CD Setup
In order for the deploy user to be able to update the docker image, make sure to add the deploy user 
to the docker group.
```
adduser deploy docker
```


Routes
===============

`/` Home page  
`/[namespace]/[numeric-identifier]` Item page (ex: `etd/100`)  
`/[full-identifier]` Item page (ex: `/etd:100`)  
    Note: redirects to the `/[namespace]/[numeric-identifier]` route  
`/search` Search results page  
`/[node-name]` Other content page or collection home page (ex: `/etd` or `/about`)  
`/[namespace]/[node-name]` Content page with in the namespace  
`iiif/[identifier]/[path]` Provide the pid and IIIF 2.0 path to render a file from the IIIF server  

Note: root pids will continue to be handled in apache

All routes are dynamically added as needed by the `route_configs` 
json files within the `instance` directory of the project. The `route` variable 
in that file defines what route rule will be associated with the contents 
of that file. Variable names can be included in the rules, which will be 
available for use in the `data` section via the `view_arg` variable.  

All that is needed to add a new content page or type is to create a new 
`route_configs` file and it's corresponding template.

For file streaming, instead of providing a `template` variable in the config 
provide a `steam` variable, which will reference a `name` field within the 
data section below.

Docker
===============

### Containers  
* **sandhill**: will run the Sandhill Flask application, exposing port 8080
* **nginx**: will run Nginx to host the sandhill's service socket (from 8080), exposing port 81
