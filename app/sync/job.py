#
# Copyright (c) 2020 Yves Vogl
#

import threading
import docker
from termcolor import colored
from hurry.filesize import size
import sys
import urllib3

class Job:
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def log(self, message):
    print(f'{threading.current_thread().ident}: {message}')

  def run(self):
    try:

      client = docker.from_env()

      self.log(f'Pulling {colored(self.source_image_url, "yellow")}')

      image = client.images.pull(
        self.source_repository,
        tag = self.source_image_tag,
        auth_config = {
          'username': self.source_username,
          'password': self.source_password
        }
      )

      self.log(f'Tagging with {colored(self.target_image_url, "green")}')

      image.tag(
        self.target_repository,
        tag = self.target_image_tag,
      )

      for line in client.images.push(
        self.target_repository,
        tag = self.target_image_tag,
        auth_config = {
          'username': self.target_username,
          'password': self.target_password
        },
        stream = True,
        decode = True
      ):
        if 'id' in line:
          if 'total' in line['progressDetail']:

            current   = line["progressDetail"]["current"]
            total     = line["progressDetail"]["total"]
            remaining = total - current
            percent   = round(current / (total / 100), 1)

            self.log(
              f'{line["status"]} {line["id"]}: {percent}% {size(remaining)}'
            )

          else:
            self.log(
              f'{line["status"]} {line["id"]}'
            )
        else:
          self.log(
            f'{line["status"]}'
          )

      return True

    except docker.errors.APIError as error:
      self.log(print(colored(error, 'red')))
    except OSError as error:
      self.log(print(colored(error, 'red')))
    except urllib3.exceptions.ReadTimeoutError as error:
      self.log(print(colored(error, 'red')))
    except socket.timeout as error:
      self.log(print(colored(error, 'red')))
    except:
      self.log(print(colored(f'Unexpected error: {sys.exc_info()[0]})', 'red')))
      raise

    finally:
      pass

  def __call__(self):
    self.run()
