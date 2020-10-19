#
# Copyright (c) 2020 Yves Vogl
#

import boto3
import boto3.session
import base64

from .repository import Repository

class Registry:

  def __init__(self,
    registry_id,
    profile_name = None,
    region_name = "eu-central-1",
    role_arn = None,
    role_session_name = None):

    self._repositories = []
    self._endpoint = None
    self._username = None
    self._password = None

    session = boto3.session.Session(
      region_name = region_name,
      profile_name = profile_name
    )

    if role_arn != None:
      response = session.client('sts').assume_role(
        RoleArn = role_arn,
        RoleSessionName = role_session_name
          if role_session_name != None
          else f'registry-synchronizer-{registry_id}',
      )

      session = boto3.session.Session(
        region_name = region_name,
        profile_name = profile_name,
        aws_access_key_id = response['Credentials']['AccessKeyId'],
        aws_secret_access_key = response['Credentials']['SecretAccessKey'],
        aws_session_token = response['Credentials']['SessionToken']
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

  # FIXME: This method should be mixed in as its not specfic to ECR
  def includes(self, repository, ignore_namespace = False, transformation = None, repositories = None):

    repository_names = self.repository_names(ignore_namespace)

    for repository_name in repository_names:

      a = transformation(repository.name(ignore_namespace)) if transformation != None else repository.name(ignore_namespace)
      b = repository_name

      if a == b:
        matched_repository = next((repo for repo in self.repositories if repo.name(ignore_namespace) == repository_name), None)

        if matched_repository != None and repositories != None:

          if matched_repository.name(ignore_namespace = True) in repositories:
            return matched_repository
          else:
            return None
        else:
          return matched_repository


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

    # FIXME: Make iterable
    if self._repositories == []:
      for repo in self._client.describe_repositories(
        registryId = self._registry_id,
        maxResults = 1000
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
