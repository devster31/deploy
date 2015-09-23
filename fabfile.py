#!/usr/bin/env python
"""
angryitalian.com fabfile
Requires additional setup for file permission and deploy user
"""
from StringIO import StringIO
import time
from os.path import join, dirname
from dotenv import load_dotenv, parse_dotenv
from fabric.api import env, run, task
from fabric.context_managers import cd, settings
from fabric.operations import put, get

__status__ = "testing"

env_file = join(dirname(__file__), '.env')
load_dotenv(env_file)

local_vagrant = 'vagrant@192.168.200.200'
# absolute path to the location of .env on remote server
env.dotenv_path = '/home/me/webapps/myapp/myapp/.env'
# env.hosts = ['104.236.85.162']
# env.user = 'deployer'
# env.key_filename = '~/.ssh/id_deployex'
code_dir = '/var/www/deploy-stage'
app_dir = '/var/www/application'
repo = 'git@github.com:Servers-for-Hackers/deploy-ex.git'
timestamp = time.strftime('%d-%m-%Y_%H:%M', time.gmtime())


@task
def vagrant():
    env.hosts = [local_vagrant]
    env.user = 'vagrant'
    env.password = 'vagrant'


# @hosts(local_vagrant)
@task
def remote_run():
    run('uname -a')


@task
def config(action=None, key=None, value=None):
    """
    Manage project configuration via .env
    see: https://github.com/theskumar/python-dotenv
    e.g: fab config:list
         fab config:set,[key],[value]
         fab config:get,hello
         fab config:unset,hello
    """
    run('touch %(dotenv_path)s' % env)
    command = 'dotenv'
    command += ' -f %s ' % env.dotenv_path
    command += action + " " if action else " "
    command += key + " " if key else " "
    command += value if value else ""
    run(command)


def sync_env():
    # env_var_dict = dict(parsed).items()
    mem_file = StringIO()
    # todo add remote environment path
    get(remote_path, mem_file)
    remote_env = mem_file.getvalue()
    local_env = list(parse_dotenv(env_file))
    for k, v in remote_env:
        for local_k, local_v in local_env:
            if local_k == k:
                if local_v == v:
                    continue
                else:
                    config('set', k, v)


@task
def sync_env2():
    with settings(mirror_local_mode=True):
        put(env_file, app_dir+'/.env')


def deploy():
    fetch_repo()
    run_composer()
    update_permissions()
    update_symlinks()


def fetch_repo():
    with cd(code_dir):
        with settings(warn_only=True):
            run("mkdir releases")
    with cd("%s/releases" % code_dir):
        run("git clone %s %s" % (repo, timestamp))


def run_composer():
    with cd("%s/%s" % (code_dir, timestamp)):
        run("composer install --prefer-dist")


def update_permissions():
    with cd("%s/releases/%s" % (code_dir, timestamp)):
        run("chgrp -R www-data .")
        run("chmod -R ug+rwx .")


def update_symlinks():
    with cd(code_dir):
        run("ln -nfs %s %s" % (code_dir+'/releases/'+timestamp, app_dir))
        run("chgrp -h www-data %s" % app_dir)
