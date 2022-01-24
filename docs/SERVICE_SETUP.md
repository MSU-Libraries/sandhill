Service Setup
==============

### Create the service
If you are running on a Linux environment, you can have Sandhill automatically start on
boot by having it defined as a service. Copy the sample systemd unit file and be sure to make
any local changes to it required for your environment (such as the `EnvironmentFile` or `WorkingDirectory`).

```
# For UWSGI setup
cp etc/systemd/system/sandhill.service /etc/systemd/system/sandhill.service
# Not required for Docker Swarm

# Enable and start the service
systemctl daemon-reload
systemctl enable sandhill
systemctl start sandhill
```

#### Create the rsyslog config (optional)
This step is required if you want to have logging for this application go to
a file other than syslog when running it as a service. This is only because `StandardOutput` and `StandardError`
support file redirection in only the very recent versions of systemd.

```
cp etc/rsyslog.d/sandhill.conf /etc/rsyslog.d/
mkdir -p /var/log/sandhill
chown -R syslog:adm /var/log/sandhill
systemctl restart rsyslog
```

### Docker Configuration:
In order to pass custom configurations to the Docker container, you will need to pass it
environment values. You can either pass them directly to the docker command
(`DEBUG=1 docker-compose up`) or provide them in an environment file,
`./.env`. See [Docker's documentation](https://docs.docker.com/compose/env-file/)
about the environment file. 

There are some default environment variable settings in
[sandhill/sandhill.default_settings.cfg](sandhill/sandhill.default_settings.cfg); using the same variable
names in the environment file will allow you to override those. 

#### Configuring email for Docker (optional):
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

