Service Setup
==============

### Create the service
If you are running on a Linux environment, you can have Sandhill automatically start on
boot by having it defined as a service. Copy the sample systemd unit file and be sure to make
any local changes to it required for your environment (such as the `EnvironmentFile` or `WorkingDirectory`).

```
# For UWSGI setup
cp etc/systemd/system/sandhill.service /etc/systemd/system/sandhill.service
# For Docker setup
cp etc/systemd/system/sandhill-docker.service /etc/systemd/system/sandhill.service

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
