# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function

import logging
import os
import subprocess
import sys
import tempfile

import yaml

from mozbitbar import cli, log, recipe_handler


logger = logging.getLogger('mozbitbar')


def build_test_archive(args):
    build_status = subprocess.check_call([
        'bash',
        os.path.join(args.mozilla_bitbar_docker_dir, 'build.sh')
    ])

    if build_status:
        print('Could not build test archive.')
        sys.exit(build_status)

    version_path = os.path.join(args.mozilla_bitbar_docker_dir, 'version')
    with open(version_path, 'r') as f:
        docker_version = f.read().rstrip()

    mozilla_docker_zip = os.path.join(args.mozilla_bitbar_docker_dir,
                                      'build',
                                      'mozilla-docker-%s.zip' % docker_version)
    if not os.path.exists(mozilla_docker_zip):
        logger.critical('%s not found.' % mozilla_docker_zip)
        sys.exit(1)
    return os.path.abspath(mozilla_docker_zip)

def _find_action_in_recipe(action, recipe):
    for index, item in enumerate(recipe):
        if item.get('action') == action:
            return index
    return None


def update_recipe(args, mozilla_docker_zip):
    testdroid_apk = os.path.abspath(args.testdroid_apk)
    with open(args.recipe, 'r') as f:
        recipe = yaml.load(f.read())

    logger.debug('Recipe found: {}'.format(args.recipe))
    index = _find_action_in_recipe('upload_file', recipe)

    if index:
        logger.debug('Recipe: upload file action found.')
        recipe[index]['arguments'] = {
                'application_filename': testdroid_apk,
                'test_filename': mozilla_docker_zip,
            }
    else:
        logger.debug('Recipe: upload file action not found.')
        action = {
            'action': 'upload_file',
            'arguments': {
                'application_filename': testdroid_apk,
                'test_filename': mozilla_docker_zip,
            }
        }
        recipe.insert(-2, action)

    recipefile = tempfile.NamedTemporaryFile(delete=False)
    yaml.dump(recipe, recipefile, default_flow_style=False)
    recipefile.close()
    return recipefile.name


def build_image_on_bitbar(recipe_path):
    logger.debug('Run mozbitbar recipe parser.')
    recipe_handler.run_recipe(recipe_path)


def main(argv):
    parser = cli.get_parser()
    parser.prog = 'generate_and_run_recipe.py'
    parser.description = "Executes Bitbar Docker builder to update mozilla image."
    parser.add_argument('--mozilla-bitbar-docker-dir',
                        required=True,
                        help='Path to mozilla-bitbar-docker Docker definition directory.')
    parser.add_argument('--testdroid-apk',
                        required=True,
                        help='Path to local copy of https://github.com/bitbar/bitbar-samples/blob/master/apps/builds/Testdroid.apk.')
    args, remainder = parser.parse_known_args(argv)

    if args.recipe is None:
        parser.error('--recipe must specify an existing mozbitbar recipe file.')
    if not os.path.exists(args.testdroid_apk):
        parser.error('--testdroid-apk %s does not exist.' % args.testdroid_apk)

    log.setup_logger(**vars(args))
    logger.info('Logging started')

    mozilla_docker_zip = build_test_archive(args)
    recipe_path = update_recipe(args, mozilla_docker_zip)
    build_image_on_bitbar(recipe_path)
    os.unlink(recipe_path)

if __name__ == '__main__':
    main(sys.argv[1:])
