# -*- coding: utf-8 -*-
import os
import subprocess
import sys

class Reporter(object):
    def run(self, apps_locations, **options):
        path = os.path.join(options['output_dir'], 'lettuce.xml')
        cmd = [sys.executable, 'manage.py', "harvest", "--with-xunit", "--xunit-file", path]

        if len(apps_locations) > 0:
            cmd.append("--apps")
            split_path_tails = []

            for app in apps_locations:
                split_path_tails.append(os.path.basename(app))

            cmd.append(",".join(split_path_tails))

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        report_output, err = process.communicate()

        retcode = process.poll()
        if retcode not in [0, 1]:  # normal sloccount return codes
            raise subprocess.CalledProcessError(retcode, cmd, output='%s\n%s' % (report_output, err))
