# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from optparse import make_option


class Reporter(object):
    option_list = (
        make_option('--lettuce-verbosity',
                    type=int,
                    dest='lettuce_verbocity',
                    help='--verbocity value when calling harvest',
                    default=0),

        make_option('--lettuce-output',
                    dest='lettuce_output',
                    help='--xunit-file value when calling harvest',
                    default='lettuce.xml'),

        make_option('--print-coverage',
                    action='store_true',
                    dest='print_coverage',
                    help='Whether to print the coverage report'),
    )


    def __init__(self, *args, **kwargs):
        super(Reporter, self).__init__(*args, **kwargs)
        self.original_coverage_file = None


    def add_arguments(self, parser):
        parser.add_argument('--lettuce-verbosity',
                            type=int,
                            dest='lettuce_verbocity',
                            help='--verbocity value when calling harvest',
                            default=0)

        parser.add_argument('--lettuce-output',
                            dest='lettuce_output',
                            help='--xunit-file value when calling harvest',
                            default='lettuce.xml')

        parser.add_argument('--print-coverage',
                            action='store_true',
                            dest='print_coverage',
                            help='Whether to print the coverage report')

    def run(self, apps_locations, **options):
        path = os.path.join(options['output_dir'], options['lettuce_output'])
        cmd = [sys.executable, 'manage.py', 'harvest', '--verbosity',
               str(options['lettuce_verbocity']), '--with-xunit', '--xunit-file',
               path]

        self.original_coverage_file = None

        if 'enable_coverage' in options and options['enable_coverage'] is True:
            cmd = self.modify_cmd_to_include_coverage(
                cmd=cmd,
                apps_locations=apps_locations,
                **options)

        #specifying the apps to test
        if len(apps_locations) > 0:
            cmd.append("--apps")
            split_path_tails = []

            for app in apps_locations:
                split_path_tails.append(os.path.basename(app))

            cmd.append(",".join(split_path_tails))

        #running the test
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        stdout = None
        retcode = None

        while True:
            stdout = process.stdout.readline()
            retcode = process.poll()

            if retcode is not None:
                break

            if stdout != "" and options['lettuce_verbocity'] > 0:
                print(stdout.strip('\n\r'))

        if 'enable_coverage' in options and options['enable_coverage'] is True:
            self.generate_coverage_reports(
                apps_locations=apps_locations,
                **options)

        if retcode not in [0, 1]:  # normal sloccount return codes
            raise subprocess.CalledProcessError(retcode, cmd,
                                                output='%s' % (stdout))


    def modify_cmd_to_include_coverage(self, cmd, apps_locations, **options):
        """
        Modifies the given cmd array so code coverage is included
        """

        self.original_coverage_file = os.environ.get('COVERAGE_FILE', None)
        os.environ['COVERAGE_FILE'] = os.path.join(options['output_dir'],
                                                   'lettuce.coverage')

        cmd[0] = os.path.join(os.path.split(cmd[0])[0], 'coverage')

        app_base = os.path.join(options['output_dir'], '../')

        #if apps are specified, then only include those apps
        if len(apps_locations) > 0:
            for app in apps_locations:
                cmd.insert(1, app)
                cmd.insert(1, '--source')

        #we want to remove from of the base cruft that we know shouldn't be
        #included
        else:
            patterns_to_ommit = [
                '*wsgi.py',
                'manage.py'
            ]

            for pattern in patterns_to_ommit:
                cmd.insert(1, pattern)
                cmd.insert(1, '--omit')

            #making sure the app is what is actually covered and not the
            #environment
            cmd.insert(1, app_base)
            cmd.insert(1, '--source')

        coverage_results = os.path.join(options['output_dir'],
                                        'lettuce.coverage')

        cmd.insert(1, 'run')
        return cmd


    def generate_coverage_reports(self, apps_locations, **options):
        """
        Generates the actual coverage reports
        """

        cmd = [os.path.join(os.path.split(sys.executable)[0], 'coverage')]

        if 'xml' in options['coverage_format']:
            coverage_results = os.path.join(options['output_dir'], 'lettuce.coverage.xml')
            cmd.append('xml')
            cmd.append('-o')
            cmd.append(coverage_results)

        if 'html' in options['coverage_format']:
            coverage_results = os.path.join(options['output_dir'], 'lettuce.coverage.html')
            cmd.append('html')
            cmd.append('-o')
            cmd.append(coverage_results)

        if options['print_coverage']:
            print('\nGenerating lettuce coverage reports...\n')

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()

        if options['print_coverage']:
            cmd = [cmd[0], 'report']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = None
            coverage_retcode = None

            while True:
                stdout = process.stdout.readline()
                coverage_retcode = process.poll()

                if coverage_retcode is not None:
                    break

                if stdout != "":
                    print(stdout.strip('\n\r'))

        #removing coverage output
        os.unlink(os.environ['COVERAGE_FILE'])

        if self.original_coverage_file is not None:
            os.environ['COVERAGE_FILE'] = self.original_coverage_file

        elif 'COVERAGE_FILE' in os.environ:
            del os.environ['COVERAGE_FILE']

