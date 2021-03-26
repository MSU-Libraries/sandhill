Sandhill
========

Sandhill is an developer oriented web application platform designed to make creating complex content fast and easy, while maintaining no-hassle extensibility. Written in Python around the Flask mico-framework, Sandhill is designed to allow rapid deployment of new features while maintaining a simple, decoupled development codebase.  

* [About Sandhill](#about-sandhill)
* [Installation](#installation)
* [Next Steps](#next-steps)

## About Sandhill
Sandhill was created by a development team at Michigan State University Libraries stemming from a goal to create a flexible front-end environment for their Digital Repository site. To accomodate for exptected repository backend changes, Sandhill was deveoped as a platform where it would be easy to adapt to major changes without requiring major software rewrites.  

Sandhill isn't a pre-built solution for repositories, but a lightweight platform to allow for rapid development your own application, whatever the purpose.   

**What does the name Sandhill mean?**  
Sandhill was named for the Sandhill Crane, a migratory bird that spends part of its time in Michigan. The origin of Sandhill came from the need to develop a frontend of MSU Libraries' Digital Repostory, which could be considered a swamp of information and the Sandhill Crane could easily live and navigate in such a vast wetlands of knowledge.  

**What technologies is Sandhill built upon?**  
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
Install the required packages to setup Sandhill (note the required `sudo` privileges for these commands only):
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

You're now ready to dive into Sandhill. Head over and read through the [Next Steps](#next-steps) you
can take to start development of your Sandhill application.  
  


### Running Sandhill in Docker
With the Docker install of Sandhill, you'll be able to skip most of the setup to get things
running quickly, but it may require a few extra steps before you can start building content
with Sandhill.  

**Required Packages**  
You'll need both `docker` and `docker-compose` installed.
You can install both of these by following the instructions at their respective sites:  
* [Docker Install](https://docs.docker.com/get-docker/)
* [docker-compose Install](https://docs.docker.com/compose/install/)

**Getting Sandhill**  
Clone the Sandhill repository and navigate into that directory:  
```
git clone https://github.com/MSU-Libraries/sandhill.git
cd sandhill
```

**Building the Docker Image**  
Build the Sandhill image by running:  
```
docker-compose build
```

**Run Sandhill as a Container**  
Create the Sandhill container by running:  
```
docker-compose up -d
```

Go to [http://localhost:8080/](http://localhost:8080/) in your browser. If everything worked, you will see a default "It Works!" page. Congratulations - you've got Sandhill up and running!  

To stop the Sandhill container, run the followin while in the `sandhill/` directory you cloned from git:  
```
docker-compose down
```

You're now ready to dive into Sandhill. Head over and read through the [Next Steps](#next-steps) you
can take to start development of your Sandhill application.  

## Next Steps
Now that the core Sandhill application is working, you are ready to set up your own
application instance. Have a look through the following documentation to help you
on your way.  

* [And Introductory Overview of Sandhill](docs/OVERVIEW.md)
* [Configuring Sandhill](docs/INSTANCE_SETUP.md)
* [Creating Content in Sandhill](docs/USER_GUIDE.md)
* [Development within your Sandhill Application](docs/DEV_GUIDE.md)
* [Running Sandhill as a Service](docs/SERVICE_SETUP.md)
* [Contributing to Sandhill](CONTRIBUTING.md)

If you have further questions or comment, please reach out to the development
team at <a href="mailto:LIB.DL.repoteam@msu.edu">LIB.DL.repoteam@msu.edu</a>.  
