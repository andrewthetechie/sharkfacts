#!/usr/bin/env python
# encoding: utf-8
import yaml
import os
import sys
import uuid
import logging
import logging.config
import random
from bottle import run, post

CONFIG = None
FACTS = None


# Production configuration
class Config(object):
    def __init__(self):
        """ Shark variables """
        self.FACT_FILE = _get_config('FACT_FILE', '/facts.txt')
        self.BIND_IP = _get_config('BIND_IP', '0.0.0.0')
        self.BIND_PORT = _get_config('BIND_PORT', 5000)

        """Logging Variables"""
        self.LOGGING_CONFIG = _get_logging_config()
        logging.config.dictConfig(self.LOGGING_CONFIG)
        self.LOGGER = logging.getLogger('sharkfacts')


class InvalidConfigException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NonBooleanStringException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def _get_config(key, default_value=None, required=False):
    """
    Gets config from environment variables
    Will return default_value if key is not in environment variables
    :param key: the key of the env variable you are looking for
    :param default_value: value to return if key not in os.environ.
    :param required: if true and key is not set, will raise InvalidConfigException
    :return: os.environ[key] if key in os.environ els default_value
    :exception InvalidConfigException - raised when a required config key is not properly set
    """
    if required and key not in os.environ:
        raise InvalidConfigException("Invalid ENV variable. Please check {0}".format(key))
    to_return = os.environ.get(key, default_value)
    if isinstance(to_return, basestring):
        try:
            to_return = _string_to_bool(to_return)
        except NonBooleanStringException:
            pass
    os.environ[key] = str(to_return)
    return to_return


def _get_logging_config():
    """
    returns a logging config Dict
    :return: Dict
    """

    _sys_log_handler_key = 'sys-logger6'
    _syslog_handler_config = {
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'facility': "local6",
                'formatter': 'verbose',
            }

    _file_handler_key = 'file-handler'
    _file_handler_config = {
                    "class": "logging.FileHandler",
                    "formatter": "verbose",
                    "filename": _get_config('LOG_FILE', '/tmp/sharkfacts.log')
                }

    _base_logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s - %(levelname)s %(module)s P%(process)d T%(thread)d %(message)s'
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose',
            }

        },
        'loggers': {
            'halp': {
                'handlers': ['stdout'],
                'level': _get_logging_level(),
                'propagate': True,
            },
        }
    }

    log_type = _get_config('LOG_TYPE', 'STDOUT').lower()

    to_return = _base_logging_config
    if log_type == 'syslog':
        to_return['handlers'][_sys_log_handler_key] = _syslog_handler_config
        to_return['loggers']['halp']['handlers'].append('sys-logger6')
    if log_type == 'file':
        to_return['handlers'][_file_handler_key] = _file_handler_config
        to_return['loggers']['halp']['handlers'].append('file-handler')

    return to_return


def _get_logging_level():
    """
    Converts our ENV variable HA_LOG_LEVEL to a logging level object
    :return: logging level object
    """
    _log_level = _get_config('LOG_LEVEL', 'info').lower()

    to_return = logging.INFO

    if _log_level == 'critical':
        to_return = logging.CRITICAL
    if _log_level == 'error':
        to_return = logging.ERROR
    if _log_level == 'warning':
        to_return = logging.WARNING
    if _log_level == 'debug':
        to_return = logging.DEBUG

    return to_return


def _string_to_bool(string):
    to_return = None
    if string.lower() in ('true', 't'):
        to_return = True
    if string.lower() in ('false', 'f'):
        to_return = False

    if to_return is None:
        raise NonBooleanStringException(string)

    return to_return


def _generate_csrf_token():
    """
    Generates a csrf token
    :return: String token
    """
    token = str(uuid.uuid4()) + str(uuid.uuid4())
    token = token.replace("-", "")
    return token


@post('/sharkfact')
def sharkfact():
    return _get_sharkfact(return_type='json')


def _get_sharkfact(return_type='text'):
    """
    Returns a random fact from our FACTS variable
    :param return_type: string, can be text for plaintext or json
    :return: Random shark fact
    """
    to_return = "Error! I can't find a shark fact for you :("
    global FACTS
    if return_type.lower() == 'text':
        to_return = random.choice(FACTS)
    if return_type.lower() == 'json':
        fact = random.choice(FACTS)
        fact_json = {
            'response_type': 'in_channel',
            'text': fact
        }
        to_return = fact_json

    return to_return


def _load_facts(file):
    """
    Loads facts from a file, one per line
    :param file: String, path to file
    :return: none
    """
    global FACTS
    with open(file) as file_handler:
        FACTS = file_handler.readlines()

if __name__ == '__main__':
    CONFIG = Config()
    _load_facts(CONFIG.FACT_FILE)
    run(host=CONFIG.BIND_IP, port=CONFIG.BIND_PORT)