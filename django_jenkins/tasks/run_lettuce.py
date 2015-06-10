# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from optparse import make_option


class Reporter(object):
    option_list = (
        make_option('--lettuce-verbosity',
                    dest='lettuce_verbocity',
                    help='--verbocity value when calling harvest',
                    default='1'),

        make_option('--lettuce-output',
                    dest='lettuce_output',
                    help='--xunit-file value when calling harvest',
                    default='lettuce.xml'),
    )

    def add_arguments(self, parser):
        parser.add_argument('--lettuce-verbosity',
                            dest='lettuce_verbocity',
                            help='--verbocity value when calling harvest',
                            default='1')

        parser.add_argument('--lettuce-output',
                            dest='lettuce_output',
                            help='--xunit-file value when calling harvest',
                            default='lettuce.xml')

    def run(self, apps_locations, **options):
        path = os.path.join(options['output_dir'], options['lettuce_output'])
        cmd = [sys.executable, 'manage.py', 'harvest', '--verbosity',
               options['lettuce_verbocity'], '--with-xunit', '--xunit-file',
               path]

        if len(apps_locations) > 0:
            cmd.append("--apps")
            split_path_tails = []

            for app in apps_locations:
                split_path_tails.append(os.path.basename(app))

            cmd.append(",".join(split_path_tails))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        stdout = None
        retcode = None

        while True:
            stdout = process.stdout.readline()
            retcode = process.poll()

            if retcode is not None:
                break

            if stdout != "":
                print(stdout.strip('\n\r'))

        if retcode not in [0, 1]:  # normal sloccount return codes
            raise subprocess.CalledProcessError(retcode, cmd,
                                                output='%s' % (stdout))
