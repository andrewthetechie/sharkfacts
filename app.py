#!/usr/bin/env python
# encoding: utf-8
import logging
import yaml
import os
import sys
import random
import json
from bottle import run, post
from cerberus import Validator

CONFIG = None
FACTS = None

class Config(object):
    def __init__(self):
        self.CONFIG_FILE = None
        self.LOGGING_CONFIG = None
        self.LOGGER = None
        pass

    def set_logger(self, logger):
        self.LOGGER = logger

    def find_config_file(self):
        if os.path.exists('./sharkfacts.conf'):
            self.CONFIG_FILE = './sharkfacts.conf'
            return

        if os.path.exists('/etc/sharkfacts/sharkfacts.conf'):
            self.CONFIG_FILE = '/etc/sharkfacts/sharkfacts.conf'
            return

        print "No valid config file. Please place one either in this directory or /etc/sharkfacts/sharkfacts.conf"
        sys.exit(1)

    def load_config(self, config_file):
        """
        Loads a CONFIG object, reading in variables from config_file
        :param config_file:
        """

        self.CONFIG_FILE = config_file
        schema = {
            'LOG_FILE': {'type': 'string', 'required': True},
            'FACT_FILE': {'type': 'string', 'required': True},
            'BIND_IP': {'type': 'string', 'required': True},
            'BIND_PORT': {'type': 'integer', 'required': True}
        }

        validator = Validator(schema)

        if not os.path.exists(config_file):
            print('Invalid CONFIG file')
            sys.exit(99)
        try:
            with open(config_file, 'r') as yaml_file:
                yaml_config = yaml.load(yaml_file)
        except IOError:
            print('Unable to open CONFIG file: {}'.format(config_file))
            sys.exit(99)
        except yaml.YAMLError, exc:
            print('Error in CONFIG file ({0}): {1}'.format(config_file, exc))
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print('Error position: ({}:{})'.format(mark.line + 1, mark.column + 1))
            sys.exit(99)

        if not validator.validate(yaml_config):
            print('Error in CONFIG.\n{}'.format(validator.errors))
            sys.exit(99)

        for key in yaml_config:
            setattr(self, key, yaml_config[key])

        self.LOGGING_CONFIG = {
            "version": 1,
            "handlers": {
                "fileHandler": {
                    "class": "logging.FileHandler",
                    "formatter": "myFormatter",
                    "filename": self.LOG_FILE
                }
            },
            "loggers": {
                "build_geo_conf": {
                    "handlers": ["fileHandler"],
                    "level": "INFO",
                }
            },

            "formatters": {
                "myFormatter": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
        }

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
            'text': fact,
            'attachments': [
                {
                    'fallback': fact,
                    'author_name': 'Sammy The Shark',
                    'title': 'Shark Fact!',
                    'text': fact,

                }
            ]
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
    CONFIG.find_config_file()
    CONFIG.load_config(CONFIG.CONFIG_FILE)
    _load_facts(CONFIG.FACT_FILE)
    run(host=CONFIG.BIND_IP, port=CONFIG.BIND_PORT)