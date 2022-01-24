Sandhill
========
*Sandhill is still in active development and is considered in the alpha stage*

Sandhill is an extensible platform designed to make developing data-driven web applications fast and easy. Written in Python using the Flask microframework, Sandhill is built with a decoupled codebase that allows for rapid deployment of new features. Sandhill provides tools to combine multiple data sources into web content using custom data processors. 

* [About Sandhill](#about-sandhill)
* [Installation](#installation)
* [Setting up an instance of Sandhill](#setting-up-an-instance-of-sandhill)

## About Sandhill
Sandhill was originally created by a development team at Michigan State University Libraries to provide a flexible front end for a digital repository. A key advantage of Sandhill is the ability to change back-end data sources without requiring significant rewrites of the base application.

Sandhill isn't a pre-built solution for repositories, but a lightweight platform that allows for rapid development of web applications covering a wide range of purposes.  

**What does the name Sandhill mean?**  
Sandhill was named for the Sandhill Crane, a migratory bird that spends part of its time in Michigan.

### Technology stack
Sandhill has been developed primarily with the following:

* [Python](https://www.python.org/about/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Jinja](https://jinja.palletsprojects.com/)
* [JSON](https://en.wikipedia.org/wiki/JSON)
* Ubuntu/Debian based Linux (but it should work on other Linux distros as well)

Having a grasp of all of the above technologies isn't necessary to get started with Sandhill, but being familiar with at least JSON, the Linux command line, and how an HTML template library works (even if it isn't Jinja) will help you get started with Sandhill.  

## Installation
There are two ways to install Sandhill.
 1. [Manual installation](#manual-installation)
 2. [Docker installation](#docker-installation)

### Manual installation
This installation method will get Sandhill running on your Linux machine directly. This requires a few more steps, but if you aren't familiar with Docker, this could be the easier route.  

These instructions assume you are using a Ubuntu or another Debian-based Linux and use the `apt` command. If you are familiar with another distro, the process should be very similar if you substitute another package manager. If all else fails, you can always try [running Sandhill in Docker](#docker-installation).

**Required packages**  
Install the required packages to set up Sandhill (note the required `sudo` privileges for these commands only):
```
sudo apt update
sudo apt install virtualenv python3-pip
```

**Getting Sandhill**  
Clone the Sandhill repository and navigate into that directory:
```
git clone https://github.com/MSU-Libraries/sandhill.git
cd sandhill
```

**Dependencies**  
Next create a virtual environment and install the required [pip](https://pip.pypa.io/en/stable/quickstart/) packages:
```
virtualenv -p python3 env
env/bin/pip install -r requirements.txt
```

**Running Sandhill**  
To start Sandhill, run the `uwsgi` within the application environment:
```
env/bin/uwsgi --ini uwsgi.ini
```
Go to [http://localhost:8080/](http://localhost:8080/) in your browser. If everything worked, you will see a default "It Works!" page. Congratulations - you've got Sandhill up and running! (Press Ctrl-C when you want to stop Sandhill)  

You're now ready to dive into Sandhill. Head over and read through [setting up an instance of Sandhill](#setting-up-an-instance-of-sandhill)
which will help you start development of your Sandhill application.  

### Docker installation
With the Docker install of Sandhill, you'll be able to skip most of the setup to get things
running quickly, but it may require a few extra steps before you can start building content
with Sandhill.  

**Required packages**  
You'll need both `docker` installed.
You can install Docker by following the instructions at their site:  
* [Docker Install](https://docs.docker.com/get-docker/)

**Initialize your Swarm**
To use Docker Swarm you need to initialize the Swarm on the environment you are running on:  
```
# Where <IP> is the current server's IP
docker swarm init --advertise-addr <IP> --listen-addr <IP>:2377

```

**Getting Sandhill**  
Clone the Sandhill repository and navigate into that directory:  
```
git clone https://github.com/MSU-Libraries/sandhill.git
cd sandhill
```

**Building the Docker image**  
Build the Sandhill image by running:  
```
docker build . -t sandhill:latest
```

**Run Sandhill as a container**  
Create the Sandhill container in Docker Swarm mode by running:  
```
docker stack deploy -c docker-compose.yml sandhill
```

Go to [http://localhost:8080/](http://localhost:8080/) in your browser. If everything worked, you will see a default "It Works!" page. Congratulations - you've got Sandhill up and running!  

To stop the Sandhill container, run the following while in the `sandhill/` directory you cloned from git:  
```
docker-compose down
```

You're now ready to dive into Sandhill. Head over and read through [setting up an instance of Sandhill](#setting-up-an-instance-of-sandhill)
which will help you start development of your Sandhill application.  

## Setting up an instance of Sandhill
After you install the core Sandhill application, you are ready to set up your own
application instance. The following documentation provides further instructions for setting up your own instance.  


* [Configuring Sandhill](docs/INSTANCE_SETUP.md)
* [Development within your Sandhill application](docs/DEV_GUIDE.md)
* [Running Sandhill as a service](docs/SERVICE_SETUP.md)
* [Contributing to Sandhill](CONTRIBUTING.md)

If you have further questions or comment, please reach out to the development
team at <a href="mailto:LIB.DL.repoteam@msu.edu">LIB.DL.repoteam@msu.edu</a>.  
