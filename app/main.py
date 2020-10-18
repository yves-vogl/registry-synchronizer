#
# Copyright (c) 2020 Yves Vogl
#

import yaml
import sys, getopt, os
from sync import Sync, Worker

def main(argv):

  mapfile = None

  try:
    opts, args = getopt.getopt(argv,"hm:",["mapfile="])
  except getopt.GetoptError:
    print('main.py -m <mapfile>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('main.py -m <mapfile>')
      sys.exit()
    elif opt in ("-m", "--mapfile"):

      worker = Worker()

      with open(rf'{arg}') as file:

        map = yaml.load(file, Loader=yaml.FullLoader)

        for description in map['sync']:
          sync = Sync(
            description['from']['registry_id'],
            description['to']['registry_id'],
          )

          sync.from_profile_name = description['from']['aws_profile']
          sync.to_profile_name = description['to']['aws_profile']

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
