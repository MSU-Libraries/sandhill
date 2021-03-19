Sandhill
========

* [What Sandhill can do for you](#what-sandhill-can-do-for-you)
* [Local setup](#local-setup)
* [Docker setup](#docker-setup)
* [Next steps](#next-steps)

What Sandhill can do for you
----------------------------
TODO

Local setup
----------------------------
Use this setup if you want to:
* Have a development environment that allows code changes to be made and immediately reflected on the page
* You don't want to use Docker for your application


### Install the required packages
```
apt install virtualenv python3-pip
```

In the cloned directory, create the virtual environment. Run this command as the developer's user.
```
virtualenv -p python3 env
```

Install the required Pip packages as the developer's user.
```
env/bin/pip install -r requirements.txt
```

### Configuration
Configuration parameters can be passed either in a config file or via environment variables 
on the host machine.

To see what default values will be used if none are passed see the 
[sandhill.default_settings.cfg](sandhill.default_settings.cfg) file.

##### File based
Make a copy of the default config and override any values you like.

```
cp sandhill/sandhill.default_settings.cfg instance/sandhill.cfg
```

#### Environment based
Alternatively you can modify the enivornment variables either at the host level (in 
`/etc/environment`) or at the application level (in `./.env`).

The same variables in the [sandhill.default_settings.cfg](sandhill.default_settings.cfg) file
can be set in the environment file.

#### Run the application
To get the application started up, simply run the uwsgi module:
```
env/bin/uwsgi --buffer-size=8192 --socket 127.0.0.1:8080 --protocol=http --py-autoreload 1 -w wsgi:application
```

Navigating to your browser at http://localhost:8080 you should see
a default "It Works!" page indicating that the site is working.


Docker Setup
-------------
Use this setup if you want:
* Set up a server to host the site without needing to make frequent changes to the code
* Have it running in a contained environment

### Install Docker and Docker Compose
Follow the steps on [Dockers official site](https://docs.docker.com/get-docker/) to install Docker
and then install [Docker Compose](https://docs.docker.com/compose/install/) as well.

### Build the image
Build a new image based on the current code.
```
docker-compose build
```

### Configuration
In order to pass custom configurations to the Docker container, you will need to pass it
environment values. You can either pass them in directly to the docker command
(`DEBUG=1 docker-compose up`) or provide it an environment file,
`./.env`. See [Docker's documentation](https://docs.docker.com/compose/env-file/)
about the environment file. The same variables from the
[sandhill.default_settings.cfg](sandhill.default_settings.cfg) file can be
used to override those defaults.

### Configure email (optional)
Sandhill has the ability to send emails based on a given error level,
if you wish to do this and included the relavent email variables 
in the environment step above you may need to configure your server to
allow it to send emails from it.

For example, in postfix, you would need to edit`/etc/postfix/main.cf` and update the
`mynetworks` line to include the docker network's IP range:
```
mynetworks = [existing line contents] 192.168.0.0/16
```

and then restart postfix:
```
systemctl restart postfix
```

### Run the image
Run the image in a detached mode.
```
docker-compose up -d
```

Note: If you need to manually take it down, run `docker-compose down`. 

Navigating to your browser at http://localhost:8080 you should see
a default "It Works!" page indicating that the site is working.


## Next steps
Now that the core Sandhill application is working, you are ready to setup your own
instance which will have your own URL route structure and template pages.
See the next section, [instance setup documentation](INSTANCE_SETUP.md) for further
instructions on how to do that.

You can optionally have the application setup to run automatically on boot. See 
the [service setup documentation](SERVICE_SETUP.md) for instructions on doing this
in a Debian based system.
