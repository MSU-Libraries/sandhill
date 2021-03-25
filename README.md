Sandhill
========

* [What Sandhill can do for you](#what-sandhill-can-do-for-you)
* [Local setup](#local-setup)
* [Docker setup](#docker-setup)
* [Next steps](#next-steps)

## What Sandhill can do for you
Sandhill is an open source framework developed by the Michigan State University Libraries. It's inception
came from the desire to have a truly flexible digital repository platform. Given how flexible it has been designed to be,
it could be used as any content delivery application. The goal of Sandhill is to provide you with a nicely organized
toolbox to build your application with. So let's get building!

### What do you need in order to successfully work with Sandhill?
In order to install, run, and make changes to Sandhill, you and your team need the a good working knowledge of the following:
* Python
* Flask
* Jinja
* Sass/SCSS
* HTML
* Debian-based system/server administration

In other words, this is not a framework well-suited to beginners, but rather to those with intermediate or advanced skill in these areas.

## Local setup
Use this setup if you want to:
* Have a development environment that allows you to make code changes and see them immediately 
reflected on the page
* _Not_ use Docker for your application

Note: this assumes you have 'apt' installed; generally Homebrew or Macports are used instead. We 
don't currently have Sandhill packages available for Homebrew or Macports, and there is no 
anticipated timeline for developing those. If you're not able to install apt, we suggest using 
the Docker image - see instructions below.


### Installation:
Install the required packages (note: you may need to update `apt` first):
```
apt install virtualenv python3-pip
```

Clone the sandhill repository and navigate into that directory to create the virtual environment.
Run this command as the developer's user.
```
virtualenv -p python3 env
```

Install the required Pip packages as the developer's user.
```
env/bin/pip install -r requirements.txt
```

### Configuration:
Configuration parameters can be passed either in a config file or via environment variables 
on the host machine.

To see what default values will be used if none are passed see the 
[sandhill.default_settings.cfg](sandhill.default_settings.cfg) file.

##### Using the config file:
Create a new instance directory at `sandhill/instance`. Then, copy the default config into `sandhill/instance`, and use that to override any values you like.

```
cp sandhill/sandhill.default_settings.cfg instance/sandhill.cfg
```

#### Using environment variables:
Alternatively you can modify the enivornment variables either at the host level (in 
`/etc/environment`) or at the application level (in `./.env`).

There are some default environment variable settings in [sandhill/sandhill.default_settings.cfg](sandhill/sandhill.default_settings.cfg); using the same variable names in the environment file will allow you to override those.

### Running the application:
To get the application started up, simply run the uwsgi module:
```
env/bin/uwsgi --buffer-size=8192 --socket 127.0.0.1:8080 --protocol=http --py-autoreload 1 -w wsgi:application
```

Navigating to your browser at http://localhost:8080 you should see
a default "It Works!" page indicating that the site is working.


## Docker Setup
Use this setup if you want to:
* Set up a server to host the site without needing to make frequent code changes
* Have it running in a contained environment

### Installing Docker and Docker Compose:
Follow the steps on [Docker's official site](https://docs.docker.com/get-docker/) to install Docker
and then install [Docker Compose](https://docs.docker.com/compose/install/) as well.

### Building the image:
Clone the sandhill repository then navigate into the directory to build a new image based on the latest stable Sandhill release:
```
docker-compose build
```

Test that it's working before moving on to configuration by running:
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
environment values. You can either pass them in directly to the docker command
(`DEBUG=1 docker-compose up`) or provide them in an environment file,
`./.env`. See [Docker's documentation](https://docs.docker.com/compose/env-file/)
about the environment file. 

There are some default environment variable settings in
[sandhill/sandhill.default_settings.cfg](sandhill/sandhill.default_settings.cfg); using the same variable
names in the environment file will allow you to override those. 

#### Configuring email (optional):
Sandhill has the ability to send emails based on a given error level.

If you wish to do this, and have included the relavent email variables in the environment step above, you may still need to configure your server in order to send emails from it. This includes installing an email server such as postfix.

For example, if you're using postfix, you would need to edit`/etc/postfix/main.cf` and update the
`mynetworks` line to include the docker network's IP range:
```
mynetworks = [existing line contents] 192.168.0.0/16
```

and then restart postfix:
```
systemctl restart postfix
```

### Runing the image:
Run the image in a detached mode.
```
docker-compose up -d
```

See the [docker-compose "getting started" documentation](https://docs.docker.com/compose/gettingstarted/)
for a quick overview of basic Docker functionality. To stop sandhill but leave the container there, run `docker-compose stop`.
If you need to manually take it down, run `docker-compose down`. 

Navigate in your browser to http://localhost:8080 - you should see
a default "It Works!" page indicating that the site is working.


## Next steps
Now that the core Sandhill application is working, you are ready to setup your own
instance which will have your own URL route structure and template pages.
See the next section, [instance setup documentation](INSTANCE_SETUP.md) for further
instructions on how to do that.

You can optionally have the application setup to run automatically on boot. See 
the [service setup documentation](SERVICE_SETUP.md) for instructions on doing this
in a Debian based system.
