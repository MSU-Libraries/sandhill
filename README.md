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

Developer Setup
===============
```
virtualenv -p python3 env
```

Routes
===============

home.py
`/` Home page

item.py
`/[namespace]/[numeric-identifier]` Item page (ex: `etd/100`)
`/[full-identifier]` Item page (ex: `/etd:100`)
    Note: redirects to the `/[namespace]/[numeric-identifier]` route

search.py
`/search` Search results page

collection.py
`/[node-name]` Other content page or collection home page (ex: `/etd` or `/about`)
    development note: 
    First check if template exists for the provided node-name, if so, render it.
    Else treat as a collection page and load the collection config file and use
    the configs for the given namespace

node.py
`/[namespace]/[node-name]` Content page with in the namespace

Note: root pids will continue to be handled in apache
