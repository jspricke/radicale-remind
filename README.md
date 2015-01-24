# Radicale Storage

Radicale storage backends for Remind and Abook.

## Dependencies

- [Radicale](http://www.radicale.org)
- [python-remind](https://github.com/jspricke/python-remind)
- [python-abook (optional)](https://github.com/jspricke/python-abook)

## Installation

Uses python-setuptools:
```
python setup.py install
```

## Config

```
[server]
hosts = 0.0.0.0:5232
daemon = False
ssl = True
certificate = /path/to/certificate.crt
key = /path/to/privateKey.key

[auth]
type = htpasswd
htpasswd_filename = /path/to/users
htpasswd_encryption = sha1

[rights]
type = owner_only

[storage]
type = custom
custom_handler = remind_abook
filesystem_folder = /home
remind_file = /path/to/.reminders
remind_timezone = Europe/Berlin
abook_file = /path/to/.abook/addressbook

[logging]
debug = False
full_environment = False
```

## Run

Run Radicale and add hostname:5232 to your CalCAV clients.
