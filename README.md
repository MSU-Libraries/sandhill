Sandhill
---------------

* [Developer Environment Setup](#developer-environment-setup)
* [Deployable Docker Setup](#deployable-docker-setup)
* [Routes](#routes)
* [Docker](#docker)
* [Developer Notes](#developer-notes)
* [Rollback](#rollback)
* [Metadata Configuration](instance/metadata_configs/README.md)
* [Page Creation](instance/route_configs/README.md)


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
sudo systemctl restart rsyslog
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

Developer Notes
===============
### Unit Testing
All code is expected to have a corelating unit test. In order to run the existing test 
simply do:  
```
# Running outside of the virtual environment
./env/bin/pytest

# Running within the virtual environment
pytest
```

It will search for all `test_*.py` files recursivly starting in the current working directory. 
So if you want to limit the tests run, then go into the directory you want and run the `pytest` 
command.

If you are in a sub-directory and want to view the complete coverage report showing which lines 
of code are uncovered, you could run `pytest --cov-report term-missing`

In the future, we will update the `.coveragerc` file to fail if any of the files have less than 
100% coverage, but for now it will just print them.

Rollback
===============
To rollback an environment to a previous commit, you first need to identify the commit (i.e. tag in the 
container registry) you want to rollback to.

Navigate to the [container registry](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/container_registry) 
to identify the tag you want to rollback to, which is based on the git commit. For example the image tagged 
`4f991a07` references https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/tree/4f991a07 that code base. 

Now navigate to the [environment](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/environments) and 
select the affected environment. Find the commit that matches the tag you want to rollback to and click the 
icon that looks like a refresh arrow that says "rollback environment" when you hover on it.

This will kick of the job the re-deploys that git commit to the server. The environment will stay in that state until another 
rollback to the latest (or any other) version is triggered. Another merge to the branch linked to that environment will also 
override whatever rolled back state you are in.  

