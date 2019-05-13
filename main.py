"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migratedb
"""
from docopt import docopt
import subprocess
import sys
import os

from alayatodo import app

def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError, ex:
        print ex.output
        sys.exit(1)


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/test_users.sql')
        _run_sql('resources/fixtures.sql')
        print "AlayaTodo: Database initialized."
    elif args['migratedb']:
        for migration in sorted(os.listdir('resources/migrations')):
            _run_sql(os.path.join('resources/migrations', migration))
            print "AlayaTodo: Database migration %s executed" % migration
    else:
        app.run(use_reloader=True)
