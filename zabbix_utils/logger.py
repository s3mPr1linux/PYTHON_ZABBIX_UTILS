# zabbix_utils
#
# Copyright (C) 2001-2023 Zabbix SIA
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import logging
from .utils import ZabbixAPIUtils


class EmptyHandler(logging.Handler):
    """Empty logging handler."""

    def emit(self, *args, **kwargs):
        pass


class SensitiveFilter(logging.Filter):
    """Filter to hide sensitive Zabbix info (password, auth) in logs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hide_data = ZabbixAPIUtils.hide_private

    def filter(self, record):
        record.msg = self.hide_data(record.msg)
        if record.args:
            new_args = [self.hide_data(arg) if isinstance(arg, str)
                        else arg for arg in record.args]
            record.args = tuple(new_args)

        return 1