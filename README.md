Sandhill
========

* [About Sandhill](#about-sandhill)
* [Local setup](#local-setup)
* [Docker setup](#docker-setup)
* [Next steps](#next-steps)

## About Sandhill
Sandhill is an open source framework developed by a team at Michigan State University Libraries. Our goal was to create a flexible front-end for [Fedora Commons 3.8](https://wiki.lyrasis.org/display/FEDORA38/Fedora+3.8+Documentation) that didn't rely on a web content management system. Sandhill isn't a pre-built front end; it's an organized toolbox you can use to build your own application. 

### What does the name Sandhill mean?
Sandhill was named for the sandhill crane, a migratory bird that spends part of its time in Michigan.

### What technologies are required to successfully work with Sandhill?
Sandhill relies on the following technologies:

* Python 3
* Flask
* Jinja
* Sass/SCSS
* HTML
* Ubuntu or other Debian-based servers

## Local setup
Use this setup if you want to:
* Have a development environment that allows you to make code changes and see them immediately reflected on the page
* _Not_ use Docker for your application

Note: the local setup instructions assume that you have `apt` installed. Sandhill packages are not available for Homebrew or Macports, and there is no anticipated timeline for developing those. If you're not able to install `apt`, we suggest using 
the [Docker image](#docker-setup).


### Installation:
Install the required packages (note: you may need to update `apt` first):
```
apt install virtualenv python3-pip
```

Clone the sandhill repository and navigate into that directory to create the virtual environment.
Run this command as your user (not root).
```
virtualenv -p python3 env
```

Install the required Pip packages as your user (not root).
```
env/bin/pip install -r requirements.txt
```

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

### Running the application:
To start the application, run the uwsgi module:
```
env/bin/uwsgi --buffer-size=8192 --socket 127.0.0.1:8080 --protocol=http --py-autoreload 1 -w wsgi:application
```
Go to http://localhost:8080 in your browser. If the site is working, you will see a default "It Works!" page.


## Docker Setup
Use this setup if you want to:
* Set up a server to host the site without needing to make frequent code changes
* Run Sandhill in a container

### Installing Docker and Docker Compose:
Follow the steps on [Docker's official site](https://docs.docker.com/get-docker/) to install Docker and [Docker Compose](https://docs.docker.com/compose/install/).

### Building the image:
Clone the sandhill repository, then navigate into the directory to build a new image based on the latest stable Sandhill release:
```
docker-compose build
```

Test that it's working by running:
```
SECRET_KEY='Testing' docker-compose up
```

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

### Running the image:
Run the image in a detached mode.
```
docker-compose up -d
```

See the [docker-compose "getting started" documentation](https://docs.docker.com/compose/gettingstarted/)
for a quick overview of basic Docker functionality. To stop Sandhill but leave the container there, run `docker-compose stop`.
If you need to manually take it down, run `docker-compose down`. 

Go to http://localhost:8080 in your browser. If the site is working, you will see a default "It Works!" page.


## Next steps
Now that the core Sandhill application is working, you are ready to set up your own
instance with a custom URL route structure and template pages.
See the [instance setup documentation](INSTANCE_SETUP.md) for instructions on setting up your own instance.

You can choose to have the application run automatically on boot. See the [service setup documentation](SERVICE_SETUP.md) for instructions on doing this in a Debian based system.
