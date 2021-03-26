Sandhill
========

Sandhill is an developer oriented web application platform designed to make creating complex content fast and easy, while maintaining no-hassle extensibility. Written in Python around the Flask mico-framework, Sandhill is designed to allow rapid deployment of new features while maintaining a simple, decoupled development codebase.  

* [About Sandhill](#about-sandhill)
* [Installation](#installation)
* [Docker setup](#docker-setup)
* [Next steps](#next-steps)

## About Sandhill
Sandhill was created by a development team at Michigan State University Libraries stemming from a goal to create a flexible front-end environment for their Digital Repository site. To accomodate for exptected repository backend changes, Sandhill was deveoped as a platform where it would be easy to adapt to major changes without requiring major software rewrites.  

Sandhill isn't a pre-built solution for repositories, but a lightweight platform to allow for rapid development your own application, whatever the purpose.   

**What does the name Sandhill mean?**  
Sandhill was named for the Sandhill Crane, a migratory bird that spends part of its time in Michigan. The origin of Sandhill came from the need to develop a frontend of MSU Libraries' Digital Repostory, which could be considered a swamp of information and the Sandhill Crane could easily live and navigate in such a vast wetlands of knowledge.  

**What technologies is Sandhill build upon?**  
Sandhill has been developed primarily with the following:

* [Python](https://www.python.org/about/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Jinja](https://jinja.palletsprojects.com/)
* [JSON](https://en.wikipedia.org/wiki/JSON)
* Ubuntu/Debian based Linux (but it should work on other Linux distos as well)

## Installation
There are two ways to get Sandhill up and running fast.
 1. [Running Sandhill Manually](#running-sandhill-manually)
 2. [Running Sandhill in Docker](#running-sandhill-in-docker)

### Running Sandhill Manually
This installation method will get Sandhill running on your Linux machine directly. This requires a few more steps, but if you aren't familiar with Docker, this could be the easier route.  

Note, we're assuming a Ubuntu or Debian based Linux here and will be using the `apt` command. If you are familiar with another distro, the process should be very similar if you just substitute the appropriate package manager command of choice. If all else fails, you can always try [Running Sandhill in Docker](#running-sandhill-in-docker).

**Required Packages**  
Install the required packages (note the required `sudo` privileges for these commands only):
```
sudo apt update
sudo apt install virtualenv python3-pip
```

Clone the Sandhill repository and navigate into that directory:
```
git clone https://github.com/MSU-Libraries/sandhill.git
cd sandhill
```

Next create a virtual environment and install the required [pip](https://pip.pypa.io/en/stable/quickstart/) packages:
```
virtualenv -p python3 env
env/bin/pip install -r requirements.txt
```

**Run Sandhill**  
To start Sandhill, run the `uwsgi` within the application environment:
```
env/bin/uwsgi --ini uwsgi.ini
```
Go to [http://localhost:8080/](http://localhost:8080/) in your browser. If everything worked, you will see a default "It Works!" page. Congratulations - you've got Sandhill up and running!  

If you'd like to start creating content at this point, head over to our [instance setup](docs/INSTANCE_SETUP.md) documentation.  

If you'd like to setup Sandhill as a service for running on a server environment, take a peek at our [service setup](docs/SERVICE_SETUP.md) guide.  

### Configuration:
Configuration parameters can be passed either in a config file or via environment variables on the host machine.

To see what default values will be used if none are passed, see the 
[sandhill.default_settings.cfg](sandhill.default_settings.cfg) file.

##### Using the config file:
Create a new instance directory at `sandhill/instance`. Then, copy the default config into `sandhill/instance` and edit the instance file to override values.

```
cp sandhill/sandhill.default_settings.cfg instance/sandhill.cfg
```

#### Using environment variables:
Alternatively, you can modify the environment variables either at the host level (in 
`/etc/environment`) or at the application level (in `./.env`).

There are some default environment variable settings in [sandhill/sandhill.default_settings.cfg](sandhill/sandhill.default_settings.cfg); using the same variable names in the environment file will allow you to override those.


### Running Sandhill in Docker
Use this setup if you want to:
* Set up a server to host the site without needing to make frequent code changes
* Run Sandhill in a container

### Installing Docker and Docker Compose:
Follow the steps on [Docker's official site](https://docs.docker.com/get-docker/) to install Docker and [Docker Compose](https://docs.docker.com/compose/install/).

### Building and running the image:
Clone the sandhill repository, then navigate into the directory to build a new image based on the latest stable Sandhill release:
```
docker-compose build
```

Test that it's working by running:
```
docker-compose up -d
```

Go to http://localhost:8080 in your browser. If the site is working, you will see a default "It Works!" page.

Once you're done, run 
```
docker-compose down
```
so that you can edit configs, etc. You'll re-do the build before you spin the application back up.

### Configuration:
In order to pass custom configurations to the Docker container, you will need to pass it
environment values. You can either pass them directly to the docker command
(`DEBUG=1 docker-compose up`) or provide them in an environment file,
`./.env`. See [Docker's documentation](https://docs.docker.com/compose/env-file/)
about the environment file. 

There are some default environment variable settings in
[sandhill/sandhill.default_settings.cfg](sandhill/sandhill.default_settings.cfg); using the same variable
names in the environment file will allow you to override those. 

#### Configuring email (optional):
Sandhill has the ability to send emails based on a given error level.

If you wish to do this, and have included the relevant email variables in the environment step above, you may still need to configure your server in order to send emails from it. This includes installing an email server such as postfix.

For example, if you're using postfix, you would need to edit`/etc/postfix/main.cf` and update the
`mynetworks` line to include the docker network's IP range:
```
mynetworks = [existing line contents] 192.168.0.0/16
```

and then restart postfix:
```
systemctl restart postfix
```

## Next steps
Now that the core Sandhill application is working, you are ready to set up your own
instance with a custom URL route structure and template pages.
See the [instance setup documentation](INSTANCE_SETUP.md) for instructions on setting up your own instance.

You can choose to have the application run automatically on boot. See the [service setup documentation](SERVICE_SETUP.md) for instructions on doing this in a Debian based system.
