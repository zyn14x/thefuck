#!/usr/bin/env python
from subprocess import call
import os
import re


version = None


def get_new_version_lines():
    global version
    with open('pyproject.toml', 'r') as pf:
        current_setup = pf.readlines()
    for line in current_setup:
        if line.startswith('version = '):
            major, minor = re.findall(r'version = "(\d+)\.(\d+)"', line)[0]
            version = "{}.{}".format(major, int(minor) + 1)
            yield 'version = "{}"\n'.format(version)
        else:
            yield line


lines = list(get_new_version_lines())
with open('pyproject.toml', 'w') as pf:
    pf.writelines(lines)

call('git pull', shell=True)
call('git commit -am "Bump to {}"'.format(version), shell=True)
call('git tag {}'.format(version), shell=True)
call('git push', shell=True)
call('git push --tags', shell=True)

env = os.environ
call('rm -rf dist/*', shell=True, env=env)
call('python -m build', shell=True, env=env)
call('twine upload dist/*', shell=True, env=env)
