from __future__ import with_statement
import os.path
from fabric.api import lcd, cd, run, require, prefix, env, task, local
from fabric.contrib.files import exists
from fabric.utils import warn
from contextlib import contextmanager as _contextmanager

env.shell = '/bin/bash -l -c'
env.repo = 'git@github.com:nikdoof/pacmanager.git'
env.local = True
env.managepath = 'pacmanager/manage.py'
env.path = os.path.dirname(__file__)

## Envs

@task
def production(alias='prod'):
    env.hosts = ['dreddit@web1.pleaseignore.com']
    env.path = '/home/dreddit/apps/pacmanager'
    env.local = False

## Common Functions

def runcmd(*args, **kwargs):
    if env.local:
        return local(*args, **kwargs)
    else:
        return run(*args, **kwargs)

@_contextmanager
def chdir(path):
    if env.local:
        with lcd(path):
            yield
    with cd(path):
        yield
        
@_contextmanager
def virtualenv():
    with chdir(env.path):
        with prefix('. %s' % os.path.join(env.path, 'env/bin/activate')):
            yield
        
def manage(args):
    """Run and Django manage.py command"""
    with virtualenv():
        runcmd('%s %s' % (env.managepath, args))    
      
## Tasks
        
@task
def virtualenv_setup():
    if not os.path.exists('env'):
        runcmd('virtualenv env')
    with virtualenv():
        runcmd('pip install -r requirements.txt')

@task
def runserver(port=3333):
    if not os.path.exists('pacmanager.db'):
        warn('No pacmanager.db found, have you syncdb?')
    ip = runcmd("""ip addr list eth0 |grep "inet " |cut -d' ' -f6|cut -d/ -f1""", capture=True)
    manage('runserver %s:%s' % (ip, port))

@task
def syncdb():
    manage('syncdb --migrate --noinput')
        
@task
def test():
    manage('test --noinput --failfast')