#
# Copyright (c) 2020 Yves Vogl
#

import yaml
import sys, getopt, os
from sync import Sync, Worker

def main(argv):

  mapfile = None
  concurrent_runs = 5

  try:
    opts, args = getopt.getopt(argv,"hm:c:",["mapfile=", "concurrency="])
  except getopt.GetoptError:
    print('main.py -m <mapfile> [-concurrency <number>]')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('main.py -m <mapfile> [-concurrency <number>]')
      sys.exit()
    elif opt in ("-m", "--mapfile"):
      mapfile = arg
    elif opt in ("-c", "--concurrency"):
      concurrent_runs = arg

  if (value := os.getenv('CONCURRENCY')) != None:
    concurrent_runs = value

  worker = Worker(concurrent_runs = concurrent_runs)

  with open(rf'{mapfile}') as file:

    map = yaml.load(file, Loader=yaml.FullLoader)

    for description in map['sync']:

      sync = Sync(
        description['from']['registry_id'],
        description['to']['registry_id'],
      )

      for key in description['from']:
        sync.__dict__.update({f'from_{key}': description['from'][key]})

      for key in description['to']:
        sync.__dict__.update({f'to_{key}': description['to'][key]})

      sync.transformations = [
        # TODO: This is potentially dangerous and needs some input sanitizing
        # See: https://stackoverflow.com/questions/11112046/create-a-lambda-function-from-a-string-properly
        eval(f"lambda x: f'{transformation}'")
        for transformation in description['transformations']
      ]

      sync.run()
      worker.add(sync.jobs)

    worker.run()


if __name__ == '__main__':
  main(sys.argv[1:])
