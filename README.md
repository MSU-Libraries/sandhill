Sandhill
---------------

* [Developer Environment Setup](#developer-environment-setup)
* [Deployable Docker Setup](#deployable-docker-setup)
* [Routes](#routes)
* [Docker](#docker)


Developer Environment Setup
===============
Use this setup if you want to set up a development environment that allows 
code changes to be made and immediately updated on the page. 

### Config setup  
Within the cloned directory, make a copy of the default config and override any values you like. 
If not specified in a separate config file, the defaults will be used. This step is not required if you 
want to use the defaults for everything. Run this command as the developer user's.  

```
cp instance/sandhill.default_settings.cfg instance/sandhill.cfg
```

### Install the required packages  
```
sudo apt install virtualenv apache2 libapache2-mod-wsgi-py3 libapache2-mod-wsgi-py3 python3-pip
```

In the cloned directory, create the virtual environment. Run this command as the developer's user. 
```
virtualenv -p python3 env
```

Install the required Pip packages as the developer's user.  
```
env/bin/pip install -r requirements.txt
```

## Create a log directory
```
sudo mkdir -p /var/log/sandhill
```

## Setup logrotate on logs
TODO

## Create the rsyslog config
This step is required to have filtered logging for only this application go to 
a file other than syslog. This is only because `StandardOutput` and `StandardError` 
do not support file redirection in Ubuntu 16.04.

```
sudo cp etc/rsyslog.d/sandhill.conf /etc/rsyslog.d/
sudo chown -R syslog:adm /var/log/sandhill
```

### Create the service
Copy the systemd unit file to set it up as a service. Be sure to make any local changes to 
it for environment specific parameters
```
sudo cp etc/systemd/system/sandhill.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sandhill
sudo systemctl start sandhill
```

### Setup Apache
Copy the apache site config and make required local changes to it.  
```
sudo cp apache2/sandhill_local.conf /etc/apache2/sites-available/sandhill.conf
sudo a2ensite sandhill.conf
sudo systemctl restart apache2
```

### Add users to docker group
In order for the users to be able to update the docker image, make sure to add their user 
to the `docker` group.
```
sudo adduser [developer_user] docker
```

### Custom Docker build
If you want to create an image to run and test outside of the CI/CD workflow, 
you can run these steps as the develop

#### Build the Image
If setting this server up through the CI/CD, skip this step.  
Build a new image based on the current code.  
```
docker-compose build
```

#### Run the Image
If setting this server up through the CI/CD, skip this step.  
Run the image in a detached mode.
```
docker-compose up -d
```

Note: If you need to manually take it down, run `docker-compose down`. TODO -- this will be moved to a service. 

To view logs of a given container just run:
```
docker container ls
docker logs -f <CONTAINER NAME>
```


Deployable Docker Setup
===============
Use this setup if you just want to set up a server to host the site without needing to make 
frequent changes to the code. 

### Install Docker
```
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common python3-pip apache2
```

Then add the key and source to apt:  
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

Finally, update apt sources and install Docker and supporting packages:  
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

### Install Docker Compose
```
sudo pip3 install docker-compose
```

### Setup Apache
Copy the apache site config and make required local changes to it.  
```
sudo cp apache/sandhill_docker.conf /etc/apache2/sites-available/sandhill.conf
sudo apache2ctl configtest
sudo a2ensite sandhill.conf
sudo systemctl reload apache2
```

### Add users to docker group
In order for the deploy user to be able to update the docker image, make sure to add the deploy user 
to the `docker` group.
```
sudo adduser deploy docker
```

### Allow the CI/CD deploy user to execute the commands on the server. Run `sudo visudo` to add:  
```
deploy ALL=(root) NOPASSWD: /bin/systemctl restart sandhill-stack.test, /bin/cp /home/deploy/sandhill/etc/systemd/system/sandhill-stack.test.service /etc/systemd/system/, /bin/systemctl daemon-reload, /bin/systemctl enable sandhill-stack.test, /bin/systemctl status sandhill-stack.test
```
TODO: long term we want to get rid of the `*` in this line, which we can do after we pull in solr to docker

### Add a UFW rule for docker access
Give the non-routable range that the docker containers use the access they need to request Fedora data.  
```
ufw allow from 192.168.0.0/16 to any port 80,443,8080 proto tcp
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
available for use in the `data` section via the `view_args` variable.  

All that is needed to add a new content page or type is to create a new 
`route_configs` file and it's corresponding template.

For file streaming, instead of providing a `template` variable in the config, 
provide a `stream` variable, which will reference a `name` field within the 
data section below.

Docker
===============

### Containers  
* **sandhill**: will run the Sandhill Flask application, exposing port 8080
* **nginx**: will run Nginx to host the sandhill's service socket (from 8080), exposing port 81
