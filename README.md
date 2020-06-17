Sandhill
---------------

Setup
===============
```
apt install python3-pip apache2 virtualenv libapache2-mod-wsgi-py3
```

Install the required Pip packages  
```
env/bin/pip install -r requirements.txt
```

Make a copy of the default config and override any values you like. If not specified 
in a separate config file, the defaults will be used. This step is not required if you 
want to use the defaults for everything.

```
cp instance/sandhill.default_settings.cfg instance/sandhill.cfg
```

Apache Setup
===============
```
apt install libapache2-mod-wsgi-py3
```

Copy the apache site config and make required local changes to it.  
```
cp sites-available/sandhill.conf /etc/apache2/sites-available/sandhill.conf
a2ensite sandhill.conf
systemctl restart apache2
```

Nginx Setup
===============
```
apt install nginx
```

Copy the system unit for Sandhill  
```
cp sandhill.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sandhill
systemctl start sandhill
```

Make a copy of the `sites-available/sandhill` and make 
required local changes to it before copying it over.  
```
cp sites-available/sandhill /etc/nginx/sites-available/sandhill
ln -s /etc/nginx/sites-available/sandhill /etc/nginx/sites-enabled
systemctl restart nginx
```

All application logs will be located in: `/var/log/nginx/sandhill.log`  
All access logs will be located in: `/var/log/nginx/sandhill-access.log`  



Developer Setup
===============
```
virtualenv -p python3 env
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

### Building the Image  
```
cd /var/www/sandhill
docker-compose build
```

### Starting the image  
```
docker-compose up -d
```
### TODO  
* have the docker compose reference an image instead of doing a build
* have logs go to a volume so we can access them and preserve them between images
