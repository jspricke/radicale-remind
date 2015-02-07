# Radicale Remind Storage

Radicale storage backends for Remind and Abook.

## Dependencies

- [Radicale](http://www.radicale.org)
- [python-remind](https://github.com/jspricke/python-remind)
- [python-abook (optional)](https://github.com/jspricke/python-abook)

## Installation

### Using pip

```
pip install radicale-remind
```

This will install all dependencies as well.

### Using python-setuptools

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
custom_handler = remind_abook_storage # or remind_storage or abook_storage
filesystem_folder = /home
remind_file = /path/to/.reminders
remind_timezone = Europe/Berlin
abook_file = /path/to/.abook/addressbook

[logging]
debug = False
full_environment = False
```
Also have a look at the [Radicale documentation](http://radicale.org/user_documentation/).

## Run

```
$ radicale
```
Add hostname:5232 to your CalCAV clients, like [DAVdroid](https://davdroid.bitfire.at/what-is-davdroid) available in [F-Droid](https://f-droid.org/).
