#
# Copyright (c) 2020 Yves Vogl
#

import subprocess
from subprocess import CalledProcessError
import threading
import os

class Job:
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def log(self, message):
    print(f'{threading.current_thread().ident}: {message}')

  def run(self):
    try:

      config_base = f'/tmp/{threading.current_thread().ident}'

      config_path_source = f'{config_base}/source'
      config_path_target = f'{config_base}/target'

      os.makedirs(config_base)

      self.log(f'Login into {self.source_registry}')
      result = self._docker_login(
        config_path_source,
        self.source_registry,
        self.source_username,
        self.source_password
      )
      result.check_returncode()
      #print(result.stdout.decode('utf-8'))

      self.log(f'Pulling {self.source_image}')
      result = self._docker_pull(
        config_path_source,
        self.source_image,
      )
      result.check_returncode()
      #print(result.stdout.decode('utf-8'))

      self.log(f'Logout {self.source_registry}')
      result = self._docker_logout(
        config_path_source
      )

      self.log(f'Tagging {self.source_image} with {self.target_image}')
      result = self._docker_tag(
        self.source_image,
        self.target_image
      )
      result.check_returncode()
      #print(result.stdout.decode('utf-8'))

      self.log(f'Login into {self.target_registry}')
      result = self._docker_login(
        config_path_target,
        self.target_registry,
        self.target_username,
        self.target_password
      )
      result.check_returncode()
      #print(result.stdout.decode('utf-8'))

      self.log(f'Pushing {self.target_image}')
      result = self._docker_push(
        config_path_target,
        self.target_image
      )
      result.check_returncode()
      print(result.stdout.decode('utf-8'))

      self.log(f'Logout {self.target_registry}')
      result = self._docker_logout(
        config_path_target
      )
      result.check_returncode()
      print(result.stdout.decode('utf-8'))

      return True

    except CalledProcessError as error:
      print(result.stderr.decode('utf-8'))
      print(error)
      raise error
    except OSError as error:
        print(error)
        raise error
    finally:
      pass
      # Leads to
      # if os.path.exists(config_base):
      #   os.remove(config_base)



  def _docker_login(self, config, endpoint, username, password):
    return subprocess.run(
      [
        'docker',
        '--config',
        config,
        'login',
        '-u',
        username,
        '--password-stdin',
        endpoint
      ],
      input=password.encode(),
      capture_output=True
    )

  def _docker_pull(self, config, image):
    return subprocess.run(
      [
        "docker",
        '--config',
        config,
        "pull",
        image
      ],
      capture_output=True
    )

  def _docker_tag(self, image, tag):
    return subprocess.run(
      [
        "docker",
        "tag",
        image,
        tag
      ],
      capture_output=True
    )

  def _docker_push(self, config, image):
    return subprocess.run(
      [
        "docker",
        '--config',
        config,
        "push",
        image
      ],
      capture_output=True
    )

  def _docker_logout(self, config):
    return subprocess.run(
      [
        "docker",
        '--config',
        config,
        "logout"
      ],
      capture_output=True
    )


  def __call__(self):
    self.run()
