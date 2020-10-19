#
# Copyright (c) 2020 Yves Vogl
#

import yaml
import sys, getopt, os
from sync import Sync, Worker

def main(argv):

  mapfile = None
  concurrent_runs = 5
  command = 'run'

  usage = 'main.py -m <mapfile> [-concurrency <number>] [--queue | --worker]'

  try:
    opts, args = getopt.getopt(argv,"hm:c:",["mapfile=", "concurrency=", "queue", "worker"])
  except getopt.GetoptError:
    print(usage)
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print(usage)
      sys.exit()
    elif opt in ("-m", "--mapfile"):
      mapfile = arg
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

      if 'limit' in description :
        number_of_images = description['limit']
      else:
        number_of_images = None

      if 'include' in description:
        repositories = description['include']['repositories']
      else:
        repositories = None

      sync.run(number_of_images = number_of_images, repositories = repositories)
      worker.add(sync.jobs)

    worker.run()


if __name__ == '__main__':
  main(sys.argv[1:])
