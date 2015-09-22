#! /usr/bin/env python
from dotenv import parse_dotenv
from os.path import join, dirname
import sys

env_file = join(dirname(__file__), '.env')


def env_check():
    parsed = parse_dotenv(env_file)
    env_var_dict = dict(parsed).items()
    env_var_list = list(parsed)
    for k, v in env_var_list:
        for local_k, local_v in env_var_list:
            if local_k == k:
                if local_v == v:
                    sys.stdout.write('same value')
                else:
                    sys.stdout.write('different value')