# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function

import logging
import os
import shutil
import subprocess
import sys
from importlib import import_module

import yaml
from testdroid import Testdroid

mozbitbar_repo = 'https://github.com/worldomonation/mozbitbar.git'
mozilla_docker_repo = 'https://github.com/bclary/mozilla-bitbar-docker.git'
clone_base_dir = os.path.dirname(os.path.abspath(__file__))
args, remainder = None, None

logger = logging.getLogger('mozbitbar')


def handle_cli(argv):
    sys.path.insert(0, os.path.join(clone_base_dir, 'mozbitbar/mozbitbar'))
    cli_handler = import_module('cli', package='mozbitbar')
    global args, remainder
    args, remainder = cli_handler.parse_arguments(argv)


def setup_logger():
    log = import_module('log', package='mozbitbar')
    log.setup_logger(**vars(args))
    logger.info('Logging started')


def clone_repository():
    if os.path.exists(os.path.join(clone_base_dir, 'mozbitbar')):
        logger.debug('Removing existing mozbitbar directory')
        shutil.rmtree(os.path.join(clone_base_dir, 'mozbitbar'))
    command = [
        'git',
        'clone',
        mozbitbar_repo,
        os.path.join(clone_base_dir, 'mozbitbar')
    ]
    # logger.info('Cloning mozbitbar')
    mozbitbar_clone_status = subprocess.check_call(command)
    if mozbitbar_clone_status:
        msg = 'Exit code for mozbitbar repository clone was \
               {}: expected 0'.format(mozbitbar_clone_status)
        # logger.critical(msg)
        print(msg)
        sys.exit(1)

    if os.path.exists(os.path.join(clone_base_dir, 'mozilla_bitbar_docker')):
        # logger.debug('Removing existing mozilla_bitbar_docker directory')
        shutil.rmtree(os.path.join(clone_base_dir, 'mozilla_bitbar_docker'))
    mozilla_docker_status = subprocess.check_call([
        'git',
        'clone',
        mozilla_docker_repo,
        os.path.join(clone_base_dir, 'mozilla_bitbar_docker')
    ])
    if mozilla_docker_status:
        print('Exit code for mozilla-docker repository clone was \
               {}: expected 0'.format(mozbitbar_clone_status))
        sys.exit(1)

    os.path.exists(os.path.join(clone_base_dir, 'mozbitbar'))
    os.path.exists(os.path.join(clone_base_dir, 'mozilla_bitbar_docker'))


def build_test_archive():
    build_status = subprocess.check_call([
        'bash',
        os.path.join(clone_base_dir, 'mozilla_bitbar_docker', 'build.sh')
    ])

    if build_status:
        print('Could not build test archive.')
        sys.exit(1)

    # version_path = os.path.join(
    #     clone_base_dir, 'mozilla-bitbar-docker', 'version')
    # with open(version_path, 'r') as f:
    #     docker_version = f.read().rstrip()


def _load_recipe():
    if args.recipe:
        with open(args.recipe, 'r') as f:
            return yaml.load(f.read())


def _write_recipe(recipe):
    if args.recipe:
        with open(args.recipe, 'w') as f:
            yaml.dump(recipe, f, default_flow_style=False)


def _find_action_in_recipe(action, recipe):
    for index, item in enumerate(recipe):
        if item.get('action') == action:
            return index
    return None


def update_test_file_name():
    if os.path.isdir(os.path.join(clone_base_dir, 'mozilla_bitbar_docker', 'build')):
        # under current naming scheme of zip files, reverse order sort will
        # place the newest archives first
        build_dir = os.path.join(
            clone_base_dir, 'mozilla_bitbar_docker', 'build')
        files = os.listdir(build_dir)
        files.sort(reverse=True)
        if len(files) > 2:
            files = files[:2]

        public_file = os.path.join(build_dir, [f for f in files if 'public' in f].pop())
        private_file = os.path.join(build_dir, [f for f in files if 'public' not in f].pop())
    else:
        print('Archive directory "build" not found on disk.')
        sys.exit(1)

    recipe = _load_recipe()
    index = _find_action_in_recipe('upload_file', recipe)

    if index:
        recipe[index]['arguments']['test_filename'] = private_file
    else:
        action = {
            'action': 'upload_file',
            'arguments': {
                'test_filename': private_file
            }
        }
        recipe.insert(-2, action)

    _write_recipe(recipe)


def build_image_on_bitbar():
    main_obj = import_module('main', package='mozbitbar')
    main_obj.main()


def run(argv):
    # clone_repository()
    handle_cli(argv)
    # setup_logger()
    # build_test_archive()
    update_test_file_name()
    build_image_on_bitbar()


if __name__ == '__main__':
    run(sys.argv[1:])
