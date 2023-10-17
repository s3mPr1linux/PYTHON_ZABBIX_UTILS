import json
import unittest
from unittest.mock import patch

from zabbix_utils.api import ZabbixAPI, ZabbixAPIVersion
from zabbix_utils.utils import ZabbixAPIUtils
from zabbix_utils.version import __min_supported__, __max_supported__
from zabbix_utils.exceptions import ZabbixAPINotSupported, ProcessingException


DEFAULT_VALUES = {
    'user': 'Admin',
    'password': 'zabbix',
    'token': 'oTmtWu',
    'session': 'cc364fb50199c5e305aa91785b7e49a0',
    'max_version': "{}.0".format(__max_supported__ + .2),
    'min_version': "{}.0".format(__min_supported__ - .2)
}


def mock_send_api_request(self, method, *args, **kwargs):
    """Mock for send_api_request method

    Args:
        method (str): Zabbix API method name.

        params (dict, optional): Params for request body. Defaults to {}.

        need_auth (bool, optional): Authorization using flag. Defaults to False.
    """
    result = {}
    if method == 'apiinfo.version':
        result = f"{__max_supported__}.0"
    elif method == 'user.login':
        result = DEFAULT_VALUES['session']
    elif method == 'user.logout':
        result = True
    elif method == 'user.checkAuthentication':
        result = {'userid': 42}
    return {'jsonrpc': '2.0', 'result': result, 'id': 1}


class TestZabbixAPI(unittest.TestCase):
    """Test cases for ZabbixAPI object"""

    def test_login(self):
        """Tests login in different auth cases"""

        test_cases = [
            {
                'input': {'token': DEFAULT_VALUES['token']},
                'output': DEFAULT_VALUES['token'],
                'exception': ProcessingException,
                'raised': False
            },
            {
                'input': {'token': DEFAULT_VALUES['token'], 'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': DEFAULT_VALUES['token'],
                'exception': ProcessingException,
                'raised': False
            },
            {
                'input': {'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': 'cc364fb50199c5e305aa91785b7e49a0',
                'exception': ProcessingException,
                'raised': False
            },
            {
                'input': {},
                'output': None,
                'exception': ProcessingException,
                'raised': True
            }
        ]

        for case in test_cases:
            with patch.multiple(
                    ZabbixAPI,
                    send_api_request=mock_send_api_request):

                zapi = ZabbixAPI(**case['input'])
                self.assertEqual(zapi.session_id, case['output'],
                                 f"unexpected output with input data: {case['input']}")
                self.assertEqual(zapi._token, case['input'].get('token'),
                                 f"unexpected output with input data: {case['input']}")

                with ZabbixAPI() as zapi:
                    try:
                        zapi.login(**case['input'])
                    except ProcessingException:
                        if not case['raised']:
                            self.fail(f"raised unexpected Exception with input data: {case['input']}")
                    else:
                        if case['raised']:
                            self.fail(f"not raised expected Exception with input data: {case['input']}")

                        self.assertEqual(zapi.session_id, case['output'],
                                        f"unexpected output with input data: {case['input']}")
                        self.assertEqual(zapi._token, case['input'].get('token'),
                                        f"unexpected output with input data: {case['input']}")

    def test_logout(self):
        """Tests logout in different auth cases"""

        test_cases = [
            {
                'input': {'token': DEFAULT_VALUES['token']},
                'output': None
            },
            {
                'input': {'token': DEFAULT_VALUES['token'], 'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': None
            },
            {
                'input': {'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': None
            }
        ]

        for case in test_cases:
            with patch.multiple(
                ZabbixAPI,
                send_api_request=mock_send_api_request):

                zapi = ZabbixAPI(**case['input'])
                zapi.logout()
                self.assertEqual(zapi.session_id, case['output'],
                                 f"unexpected output with input data: {case['input']}")
                self.assertEqual(zapi._token, case['output'],
                                 f"unexpected output with input data: {case['input']}")

    def test_check_auth(self):
        """Tests check_auth method in different auth cases"""

        test_cases = [
            {
                'input': {'token': DEFAULT_VALUES['token']},
                'output': True
            },
            {
                'input': {'token': DEFAULT_VALUES['token'], 'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': True
            },
            {
                'input': {'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'output': True
            }
        ]

        for case in test_cases:
            with patch.multiple(
                ZabbixAPI,
                send_api_request=mock_send_api_request):

                zapi = ZabbixAPI(**case['input'])
                auth = zapi.check_auth()
                self.assertEqual(auth, case['output'],
                                 f"unexpected output with input data: {case['input']}")
                zapi.logout()
                auth = zapi.check_auth()
                self.assertEqual(auth, not case['output'],
                                 f"unexpected output with input data: {case['input']}")

    def test_check_version(self):
        """Tests __check_version method with different versions"""

        with patch.multiple(
                ZabbixAPI,
                api_version=lambda s: ZabbixAPIVersion(DEFAULT_VALUES['max_version'])):

            with self.assertRaises(ZabbixAPINotSupported,
                                   msg=f"version={DEFAULT_VALUES['max_version']}"):
                ZabbixAPI()

            try: 
                ZabbixAPI(skip_version_check=True)
            except Exception:
                self.fail(f"raised unexpected Exception for version: {DEFAULT_VALUES['max_version']}")

        with patch.multiple(
                ZabbixAPI,
                api_version=lambda s: ZabbixAPIVersion(DEFAULT_VALUES['min_version'])):

            with self.assertRaises(ZabbixAPINotSupported,
                                   msg=f"version={DEFAULT_VALUES['min_version']}"):
                ZabbixAPI()

            try: 
                ZabbixAPI(skip_version_check=True)
            except Exception:
                self.fail(f"raised unexpected Exception for version: {DEFAULT_VALUES['min_version']}")

    def test_version_conditions(self):
        """Tests behavior of ZabbixAPI object depending on different versions"""

        test_cases = [
            {
                'input': {'token': DEFAULT_VALUES['token']},
                'version': '5.2.0',
                'exception': ZabbixAPINotSupported,
                'raised': True,
                'output': DEFAULT_VALUES['session']
            },
            {
                'input': {'token': DEFAULT_VALUES['token'], 'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'version': '5.2.0',
                'exception': ZabbixAPINotSupported,
                'raised': False,
                'output': DEFAULT_VALUES['session']
            },
            {
                'input': {'token': DEFAULT_VALUES['token']},
                'version': '5.4.0',
                'exception': ZabbixAPINotSupported,
                'raised': False,
                'output': DEFAULT_VALUES['token']
            },
            {
                'input': {'token': DEFAULT_VALUES['token'], 'user': DEFAULT_VALUES['user'], 'password': DEFAULT_VALUES['password']},
                'version': '5.4.0',
                'exception': ZabbixAPINotSupported,
                'raised': False,
                'output': DEFAULT_VALUES['token']
            }
        ]

        for case in test_cases:
            with patch.multiple(
                    ZabbixAPI,
                    send_api_request=mock_send_api_request,
                    api_version=lambda s: ZabbixAPIVersion(case['version'])):

                try:
                    zapi = ZabbixAPI(**case['input'])
                except Exception:
                    if not case['raised']:
                        self.fail(f"raised unexpected Exception for version: {case['version']}")
                else:
                    if case['raised']:
                        self.fail(f"not raised expected Exception for version: {case['version']}")

                    self.assertEqual(zapi.session_id, case['output'],
                                         f"unexpected output with input data: {case['input']}")


class TestZabbixAPIVersion(unittest.TestCase):
    """Test cases for ZabbixAPIVersion object"""

    def test_init(self):
        """Tests creating of ZabbixAPIVersion object"""

        test_cases = [
            {'input': '7.0.0alpha', 'output': '7.0.0alpha', 'exception': TypeError, 'raised': False},
            {'input': '6.0.0', 'output': '6.0.0', 'exception': TypeError, 'raised': False},
            {'input': '6.0', 'output': None, 'exception': TypeError, 'raised': True},
            {'input': '7', 'output': None, 'exception': TypeError, 'raised': True}
        ]

        for case in test_cases:
            try:
                ver = ZabbixAPIVersion(case['input'])
            except TypeError:
                if not case['raised']:
                    self.fail(f"raised unexpected Exception with input data: {case['input']}")
            else:
                if case['raised']:
                    self.fail(f"not raised expected Exception with input data: {case['input']}")
                self.assertEqual(str(ver), case['output'],
                                 f"unexpected output with input data: {case['input']}")

    def test_major(self):
        """Tests getting the major version part of ZabbixAPIVersion"""

        test_cases = [
            {'input': '6.0.10alpha', 'output': 6.0},
            {'input': '6.2.0', 'output': 6.2}
        ]

        for case in test_cases:
            ver = ZabbixAPIVersion(case['input'])
            self.assertEqual(ver.major, case['output'],
                             f"unexpected output with input data: {case['input']}")

    def test_minor(self):
        """Tests getting the minor version part of ZabbixAPIVersion"""

        test_cases = [
            {'input': '6.0.10alpha', 'output': 10, 'text': 'alpha'},
            {'input': '6.2.0', 'output': 0, 'text': ''}
        ]

        for case in test_cases:
            ver = ZabbixAPIVersion(case['input'])
            self.assertEqual(ver.minor, case['output'],
                             f"unexpected output with input data: {case['input']}")
            self.assertEqual(ver.text, case['text'],
                             f"unexpected output with input data: {case['input']}")

    def test_is_lts(self):
        """Tests is_lts method for different versions"""

        test_cases = [
            {'input': '6.0.10alpha', 'output': False},
            {'input': '6.2.0', 'output': False},
            {'input': '6.4.5', 'output': False},
            {'input': '7.0.0', 'output': True},
            {'input': '7.0.30', 'output': True}
        ]

        for case in test_cases:
            ver = ZabbixAPIVersion(case['input'])
            self.assertEqual(ver.is_lts(), case['output'],
                             f"unexpected output with input data: {case['input']}")

    def test_compare(self):
        """Tests version comparison for different version formats"""

        test_cases = [
            {'input': ['6.0.0','6.0.0'], 'operation': 'eq', 'output': True},
            {'input': ['6.0.0',6], 'operation': 'ne', 'output': False},
            {'input': ['6.0.0',6.0], 'operation': 'ge', 'output': True},
            {'input': ['6.0.0',7.0], 'operation': 'lt', 'output': True},
            {'input': ['6.4.1',6], 'operation': 'gt', 'output': False}
        ]

        for case in test_cases:
            ver = ZabbixAPIVersion(case['input'][0])
            result = (getattr(ver, f"__{case['operation']}__")(case['input'][1]))
            self.assertEqual(result, case['output'],
                             f"unexpected output with input data: {case['input']}")

        ver = ZabbixAPIVersion('6.0.0')
        with self.assertRaises(TypeError,
                               msg=f"input data={case['input']}"):
            ver > {}

        with self.assertRaises(TypeError,
                               msg=f"input data={case['input']}"):
            ver < []

        with self.assertRaises(TypeError,
                               msg=f"input data={case['input']}"):
            ver <= '7.0'


class TestZabbixAPIUtils(unittest.TestCase):
    """Test cases for ZabbixAPIUtils class"""

    def test_check_url(self):
        """Tests check_url method in different cases"""

        filename = ZabbixAPIUtils.JSONRPC_FILE

        test_cases = [
            {'input': '127.0.0.1', 'output': f"http://127.0.0.1/{filename}"},
            {'input': 'https://localhost', 'output': f"https://localhost/{filename}"},
            {'input': 'localhost/zabbix', 'output': f"http://localhost/zabbix/{filename}"},
            {'input': 'localhost/', 'output': f"http://localhost/{filename}"},
            {'input': f"127.0.0.1/{filename}", 'output': f"http://127.0.0.1/{filename}"}
        ]

        for case in test_cases:
            result = ZabbixAPIUtils.check_url(case['input'])
            self.assertEqual(result, case['output'],
                             f"unexpected output with input data: {case['input']}")

    def test_secreter(self):
        """Tests secreter method in different cases"""

        mask = ZabbixAPIUtils.HIDINGMASK

        test_cases = [
            {'input': {'string': 'lZSwaQ', 'show_len': 5}, 'output': mask},
            {'input': {'string': 'ZWvaGS5SzNGaR990f', 'show_len': 4}, 'output': f"ZWva{mask}990f"},
            {'input': {'string': 'KZneJzgRzdlWcUjJj', 'show_len': 10}, 'output': f"KZneJzgRzd{mask}RzdlWcUjJj"},
            {'input': {'string': 'g5imzEr7TPcBG47fa', 'show_len': 20}, 'output': mask},
            {'input': {'string': 'In8y4eGughjBNSqEGPcqzejToVUT3OA4q5', 'show_len':2}, 'output': f"In{mask}q5"},
            {'input': {'string': 'Z8pZom5EVbRZ0W5wz', 'show_len':0}, 'output': "Z8pZom5EVbRZ0W5wz"}
        ]

        for case in test_cases:
            result = ZabbixAPIUtils.secreter(**case['input'])
            self.assertEqual(result, case['output'],
                             f"unexpected output with input data: {case['input']}")

    def test_cutter(self):
        """Tests cutter method in different cases"""

        test_cases = [
            {
                'input': {'string': 'ZWvaGS5SzNGaR990f', 'max_len': 4, 'dots': True},
                'output': 'ZWva...'
            },
            {
                'input': {'string': 'KZneJzgRzdlWcUjJj', 'max_len': 10, 'dots': False},
                'output': 'KZneJzgRzd'
            },
            {
                'input': {'string': 'g5imzEr7TPcBG47fa', 'max_len': 20, 'dots': True},
                'output': 'g5imzEr7TPcBG47fa'
            },
            {
                'input': {'string': 'In8y4eGughjBNSqEGPcqzejToVUT3OA4q5', 'max_len':20, 'dots': True},
                'output': 'In8y4eGughjBNSqEGPcq...'
            },
            {
                'input': {'string': 'Z8pZom5EVbRZ0W5wz', 'max_len': 0, 'dots': True},
                'output': '...'
            },
            {
                'input': {'string': '0gtRoOSbHLZqYR3BF', 'max_len': 0, 'dots': False},
                'output': ''
            }
        ]

        for case in test_cases:
            result = ZabbixAPIUtils.cutter(**case['input'])
            self.assertEqual(result, case['output'],
                             f"unexpected output with input data: {case['input']}")

    def test_hide_private(self):
        """Tests hide_private method in different cases"""

        mask = ZabbixAPIUtils.HIDINGMASK

        test_cases = [
            {
                'input': json.dumps({"auth": "q2BTIw85kqmjtXl3","token": "jZAC51wHuWdwvQnx"}),
                'output': json.dumps({"auth": mask, "token": mask})
            },
            {
                'input': json.dumps({"token": "jZAC51wHuWdwvQnxwbP2T55vh6R5R2uW"}),
                'output': json.dumps({"token": f"jZAC{mask}R2uW"})
            },
            {
                'input': json.dumps({"auth": "q2BTIw85kqmjtXl3zCgSSR26gwCGVFMK"}),
                'output': json.dumps({"auth": f"q2BT{mask}VFMK"})
            },
            {
                'input': json.dumps({"sessionid": "p1xqXSf2HhYWa2ml6R5R2uWwbP2T55vh"}),
                'output': json.dumps({"sessionid": f"p1xq{mask}55vh"})
            },
            {
                'input': json.dumps({"password": "HlphkcKgQKvofQHP"}),
                'output': json.dumps({"password": mask})
            }
        ]

        for case in test_cases:
            result = ZabbixAPIUtils.hide_private(case['input'])
            self.assertEqual(result, case['output'],
                             f"unexpected output with input data: {case['input']}")


if __name__ == '__main__':
    unittest.main()