#
# Copyright (c) 2020 Yves Vogl
#

from termcolor import colored
from ecr import Registry
from .job import Job

class Sync():

  def __init__(self, from_registry_id, to_registry_id):

    self._from_registry_id = from_registry_id
    self._to_registry_id = to_registry_id

    self.from_profile_name = None
    self.to_profile_name = None

    self._transformations = [lambda x: x]

    self._jobs = []

  def run(self):

    from_registry = Registry(
      self._from_registry_id,
      profile_name=self.from_profile_name
    )

    to_registry = Registry(
      self._to_registry_id,
      profile_name=self.to_profile_name
    )

    return self._compare(from_registry, to_registry)

  def _compare(self, from_registry, to_registry):

    print(f'Sync matching repositories of {to_registry.url} ({len(to_registry.repositories)}) from {from_registry.url} ({len(from_registry.repositories)})')

    found = {}

    for repository in to_registry.repositories:

      for transformation in self.transformations:
        result = from_registry.includes(repository, ignore_namespace = True, transformation = transformation)

        found[repository.name()] = result

        if result:

          found[repository.name()] = {
            'name': result.name(),
            'tags': [image.tag for image in result.images]
          }

          for image in result.images:
            job = Job(
              source_registry = from_registry.url,
              source_username = from_registry.username,
              source_password = from_registry.password,
              target_registry = to_registry.url,
              target_username = to_registry.username,
              target_password = to_registry.password,
              source_image = f'{image.url}',
              target_image = f'{to_registry.name}/{repository.name()}:{image.tag}'
            )
            self._jobs.append(job)


          break

    for repo, result in found.items():

      if result != None:
        print(
          colored(f'{repo}', 'green'),
          f'is found as',
          colored(f'{result["name"]}.', 'yellow')
        )
      else:
        print(
          colored(f'{repo}.', 'red'),
          'not found.'
        )

    return found

  @property
  def jobs(self):
    return self._jobs

  @property
  def transformations(self):
    return self._transformations

  @transformations.setter
  def transformations(self, value):
    self._transformations = [lambda x: x]
    self._transformations += value
