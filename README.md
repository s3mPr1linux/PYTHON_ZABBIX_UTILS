# Zabbix utils library

**zabbix_utils** is a Python library for working with [Zabbix API](https://www.zabbix.com/documentation/current/manual/api/reference) as well as with [Zabbix sender](https://www.zabbix.com/documentation/current/manpages/zabbix_sender) and [Zabbix get](https://www.zabbix.com/documentation/current/manpages/zabbix_get) protocols.

## Get started
* [Requirements](#requirements)
* [Installation](#installation)
* [Zabbix API](#to-work-with-zabbix-api)
* [Zabbix Sender](#to-work-via-zabbix-sender-protocol)
* [Zabbix Get](#to-work-via-zabbix-get-protocol)
* [Debug log](#enabling-debug-log)

## Requirements

Supported versions:

* Zabbix 5.0+
* Python 3.10+

Tested on:

* Zabbix 4.0, 5.0, 6.0, 6.4 and 7.0
* Python 3.7, 3.8, 3.9, 3.10 and 3.11

## Documentation

### Installation

Install **zabbix_utils** library using pip:

```bash
$ pip install zabbix_utils
```

### Use cases

##### To work with Zabbix API

To work with Zabbix API  you can import and use **zabbix_utils** library as follows:

```python
from zabbix_utils import ZabbixAPI

api = ZabbixAPI(url="127.0.0.1")
api.login(user="User", password="zabbix")

users = api.user.get(
    output=['userid', 'alias']
)

for user in users:
    print(user['alias'])

api.logout()
```

You can also authenticate using an API token (supported since Zabbix 5.4):

```python
from zabbix_utils import ZabbixAPI

api = ZabbixAPI(url="127.0.0.1")
api.login(token="xxxxxxxx")

users = api.user.get(
    output=['userid', 'alias']
)

for user in users:
    print(user['alias'])

api.logout()
```

You can compare Zabbix API version with strings and numbers, for example:

```python
from zabbix_utils import ZabbixAPI

url = "127.0.0.1"
user = "User"
password = "zabbix"

api = ZabbixAPI(url=url, user=user, password=password)

# Method to get version
ver = api.api_version()
print(type(ver).__name__, ver) # ZabbixAPIVersion 7.0.0

# ZabbixAPI prototype with version
ver = api.version
print(type(ver).__name__, ver) # ZabbixAPIVersion 7.0.0

# Comparing versions
print(ver > 6.0)      # True
print(ver != 7.0)     # False
print(ver <= 7)       # True
print(ver != "7.0.0") # False

# Version additional methods
print(ver.major)    # 7.0
print(ver.minor)    # 0
print(ver.is_lts()) # True

api.logout()
```

> Please, refer to the [Zabbix API Documentation](https://www.zabbix.com/documentation/current/manual/api/reference) and the [using examples](https://github.com/zabbix/python-zabbix-utils/tree/master/examples/api) for more information.

##### To work via Zabbix sender protocol

To send item values to a Zabbix server or a Zabbix proxy you can import and use the library as follows:

```python
from zabbix_utils import ZabbixSender

sender = ZabbixSender(server='127.0.0.1', port=10051)
resp = sender.send_value('host', 'item.key', 'value', 1695713666)

print(resp)
# {"processed": 1, "failed": 0, "total": 1, "time": "0.000338", "chunk": 1}
```

Or you can prepare a list of item values and send all at once:

```python
from zabbix_utils import ZabbixItem, ZabbixSender

items = [
    ZabbixItem('host1', 'item.key1', 10),
    ZabbixItem('host1', 'item.key2', 'test message'),
    ZabbixItem('host2', 'item.key1', -1, 1695713666),
    ZabbixItem('host3', 'item.key1', '{"msg":"test message"}'),
    ZabbixItem('host2', 'item.key1', 0, 1695713666, 100)
]

sender = ZabbixSender(server='127.0.0.1', port=10051)
chunks_resp = sender.send(items)

print(chunks_resp)
# [{"processed": 5, "failed": 0, "total": 5, "time": "0.001661", "chunk": 1}]
```

> Please, refer to the [Zabbix sender protocol](https://www.zabbix.com/documentation/current/manual/appendix/protocols/zabbix_sender) and the [using examples](https://github.com/zabbix/python-zabbix-utils/tree/master/examples/sender) for more information.

##### To work via Zabbix get protocol

To get a value by item key from a Zabbix agent or agent 2 you can import and use the library as follows:

```python
from zabbix_utils import ZabbixGet

agent = ZabbixGet(host='127.0.0.1', port=10050)
resp = agent.get('system.uname')

print(resp)
# Linux test_server 5.15.0-3.60.5.1.el9uek.x86_64
```

> Please, refer to the [Zabbix agent protocol](https://www.zabbix.com/documentation/current/manual/appendix/protocols/zabbix_agent) and the [using examples](https://github.com/zabbix/python-zabbix-utils/tree/master/examples/get) for more information.

### Enabling debug log

If it needed to debug some issue with Zabbix API, sender or get you can enable the output of logging. The **zabbix_utils** library uses the default python logging module, but it logs to the `null` by default. You can define logging handler to see records from the library, for example:

```python
import logging
from zabbix_utils import ZabbixGet

logging.basicConfig(
    format=u'[%(asctime)s] %(levelname)s %(message)s',
    level=logging.DEBUG
)

agent = ZabbixGet(host='127.0.0.1', port=10050)
resp = agent.get('system.uname')

print(resp)
```

And then you can see records like the following:

```
[2023-10-01 12:00:01,587] DEBUG Content of the packet: b'ZBXD\x01\x0c\x00\x00\x00\x00\x00\x00\x00system.uname'
[2023-10-01 12:00:01,722] DEBUG Zabbix response header: b'ZBXD\x01C\x00\x00\x00C\x00\x00\x00'
[2023-10-01 12:00:01,723] DEBUG Zabbix response body: Linux test_server 5.15.0-3.60.5.1.el9uek.x86_64
[2023-10-01 12:00:01,724] DEBUG Response from [127.0.0.1:10050]: Linux test_server 5.15.0-3.60.5.1.el9uek.x86_64
Linux test_server 5.15.0-3.60.5.1.el9uek.x86_64

```

## License
**zabbix_utils** is distributed under MIT License.