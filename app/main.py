#
# Copyright (c) 2020 Yves Vogl
#

import yaml
import sys, getopt, os
from sync import Sync, Worker

def main(argv):

  mapfile = None
  number_of_images = 5
  concurrent_runs = 5
  command = 'run'

  try:
    opts, args = getopt.getopt(argv,"hm:n:c:",["mapfile=", "number-of-images=", "concurrency=", "queue", "worker"])
  except getopt.GetoptError:
    print('main.py -m <mapfile> [--number-of-images <number>] [-concurrency <number>] [--queue | --worker]')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('main.py -m <mapfile> [--number-of-images <number>] [-concurrency <number>] [--queue | --worker]')
      sys.exit()
    elif opt in ("-m", "--mapfile"):
      mapfile = arg
    elif opt in ("-n", "--number-of-images"):
      number_of_images = int(arg)
    elif opt in ("-c", "--concurrency"):
      concurrent_runs = int(arg)
    elif opt in ("-q", "--queue"):
      command = 'queue'
    elif opt in ("-w", "--worker"):
      command = 'worker'

  if (value := os.getenv('CONCURRENCY')) != None:
    concurrent_runs = value

  # print(command)
  # exit()

  worker = Worker(concurrent_runs = concurrent_runs)

  with open(rf'{mapfile}') as file:

    map = yaml.load(file, Loader=yaml.FullLoader)

    for description in map['sync']:

      sync = Sync(
        description['from']['registry_id'],
        description['to']['registry_id']
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

      sync.run(number_of_images)
      worker.add(sync.jobs)

    worker.run()


if __name__ == '__main__':
  main(sys.argv[1:])
