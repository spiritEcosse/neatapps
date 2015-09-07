__author__ = 'igor'

from fabric.api import local, run, require, cd
import os
from neatapps.settings import BASE_DIR
from fabric.state import env
env.hosts = ['root@78.24.216.187']
env.user = 'root'
PROJECT_DIR = '/home/igor/web/www/neatapps'
REQUIREMENTS_FILE = 'requirements.txt'
TORNADO_SCRIPT = 'tornado_main.py'


def deploy():
    """
    deploy project on remote server
    :return:
    """
    local_act()
    update_requirements()
    touch()


def local_act():
    """
    prepare deploy
    :return: None
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neatapps.settings")
    activate_env = os.path.expanduser(os.path.join(BASE_DIR, ".env/bin/activate_this.py"))
    execfile(activate_env, dict(__file__=activate_env))
    local("./manage.py test")
    local("%s%s" % ('pip freeze > ', REQUIREMENTS_FILE))
    # local("./manage.py collectstatic -c --noinput")
    local("git add .")
    local("git commit -a -F git_commit_message")
    current_branch = local("git rev-parse --abbrev-ref HEAD")

    if current_branch != 'master':
        # local("git checkout master")
        # local("git merge {0}".format(current_branch))
        print(current_branch)
        
    local("git push origin")
    local("git push production")
    local("git push my_repo_neatapps_bit")


def touch():
    """
    reload tornado script
    :return: None
    """
    run('touch %s' % TORNADO_SCRIPT)


def update_requirements():
    """
    install external requirements on remote host
    :return: None
    """
    with cd(PROJECT_DIR):
        run('%s && %s%s' % ('source .env/bin/activate', 'pip install -r ', REQUIREMENTS_FILE))