#
# Copyright (c) 2020 Yves Vogl
#

import boto3
import boto3.session
import base64

from .repository import Repository

class Registry:

  def __init__(self, registry_id, profile_name="default", region_name="eu-central-1"):

    self._repositories = []
    self._endpoint = None
    self._username = None
    self._password = None

    session = boto3.session.Session(
      region_name=region_name,
      profile_name=profile_name
    )

    self._registry_id = registry_id
    self._client = session.client('ecr')

    self.authorize()

  def authorize(self):

    authorization_token = self._client.get_authorization_token()['authorizationData'][0]

    self._endpoint = authorization_token['proxyEndpoint']

    self._username, self._password = base64.b64decode(
      authorization_token['authorizationToken']
    ).decode().split(':')

  def includes(self, repository, ignore_namespace = False, transformation = None):

    repository_names = self.repository_names(ignore_namespace)

    for repository_name in repository_names:

      a = transformation(repository.name(ignore_namespace)) if transformation != None else repository.name(ignore_namespace)
      b = repository_name

      #print(f'{a} -> {b}')
      if a == b:
        return next((repo for repo in self.repositories if repo.name(ignore_namespace) == repository_name), None)

  @property
  def url(self):
    return self._endpoint

  @property
  def name(self):
    return self._endpoint.replace("https://", "")

  @property
  def username(self):
    return self._username

  @property
  def password(self):
    return self._password

  @property
  def repositories(self):

    if self._repositories == []:
      for repo in self._client.describe_repositories(
        registryId=self._registry_id,
        maxResults=1000
      )['repositories']:
        repository = Repository(self, repo['repositoryName'])
        self._repositories.append(repository)

    return self._repositories

  def repository_names(self, ignore_namespace = False):
    return [
      repository.name(ignore_namespace) for repository in self.repositories
    ]

  @property
  def client(self):
    return self._client
