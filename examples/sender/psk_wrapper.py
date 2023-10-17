import ssl
from zabbix_utils import ZabbixSender

# Try importing sslpsk3, fall back to sslpsk2 if not available
try:
    import sslpsk3 as sslpsk
except ImportError:
    # Import sslpsk2 if sslpsk3 is not available
    import sslpsk2 as sslpsk


# PSK wrapper function for SSL connection
def psk_wrapper(sock, tls):
    # Pre-Shared Key (PSK) and PSK Identity
    psk = b'608b0a0049d41fdb35a824ef0a227f24e5099c60aa935e803370a961c937d6f7'
    psk_identity = b'PSKID'

    return sslpsk.wrap_socket(
        sock,
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        ciphers='ECDHE-PSK-AES128-CBC-SHA256',
        psk=(psk, psk_identity)
    )


# Zabbix server details
ZABBIX_SERVER = "127.0.0.1"
ZABBIX_PORT = 10051

# Create a ZabbixSender instance with PSK support
sender = ZabbixSender(
    server=ZABBIX_SERVER,
    port=ZABBIX_PORT,
    socket_wrapper=psk_wrapper
)

# Send a value to a Zabbix server/proxy with specified parameters
# Parameters: (host, key, value, clock, ns)
resp = sender.send_value('host', 'item.key', 'value', 1695713666, 30)

# Check if the value sending was successful
if resp.failed == 0:
    # Print a success message along with the response time
    print(f"Value sent successfully in {resp.time}")
else:
    # Print a failure message
    print("Failed to send value")