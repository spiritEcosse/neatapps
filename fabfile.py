__author__ = 'igor'

from fabric.api import local, run, cd, settings
import os
from neatapps.settings import BASE_DIR
from fabric.state import env
from neatapps.settings_local import HOSTS
env.user = 'root'
env.skip_bad_hosts = True
env.warn_only = False
env.parallel = True
env.shell = "/bin/bash -l -i -c"
REQUIREMENTS_FILE = 'requirements.txt'


def deploy():
    """
    deploy project on remote server
    :return:
    """
    local_act()
    update_requirements()
    remote_act()


def remote_act():
    """
    run remote acts
    :return: None
    """
    for host, dir_name in HOSTS:
        with settings(host_string=host):
            with cd(dir_name):
                run("git reset --hard")
                run("kill -9 $(ps -ef|grep -v grep |grep 'neatapps' | awk '{print $2}')")
                run("neatapps")


def local_act():
    """
    prepare deploy
    :return: None
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neatapps.settings")
    activate_env = os.path.expanduser(os.path.join(BASE_DIR, ".env/bin/activate_this.py"))
    execfile(activate_env, dict(__file__=activate_env))
    local("./manage.py test")
    local("./manage.py compilemessages")
    local("./manage.py makemigrations")
    local("./manage.py migrate")
    local("%s%s" % ('pip freeze > ', REQUIREMENTS_FILE))
    local("./manage.py collectstatic --noinput -c")
    local("git add .")
    local("git commit -a -F git_commit_message")
    current_branch = local("git symbolic-ref --short -q HEAD", capture=True)

    if current_branch != 'master':
        local("git checkout master")
        local("git merge %s" % current_branch)
        local("git branch -d %s" % current_branch)

    local("git push origin")
    local("git push production")
    local("git push my_repo_neatapps_bit")
    local("git push my-production")


def update_requirements():
    """
    install external requirements on remote host
    :return: None
    """
    for host, dir_name in HOSTS:
        with settings(host_string=host):
            with cd(dir_name):
                run('%s && %s%s' % ('source .env/bin/activate', 'pip install -r ', REQUIREMENTS_FILE))
