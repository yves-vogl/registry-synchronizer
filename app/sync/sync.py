#
# Copyright (c) 2020 Yves Vogl
#

from termcolor import colored
from ecr import Registry
from .job import Job


class Sync():

    def __init__(self, from_registry_id, to_registry_id):

        self._from_registry_id = from_registry_id
        self.from_aws_profile = None
        self.from_aws_region = 'eu-central-1'
        self.from_aws_role_arn = None
        self.from_aws_role_session_name = None

        self._to_registry_id = to_registry_id
        self.to_aws_profile = None
        self.to_aws_region = 'eu-central-1'
        self.to_aws_role_arn = None
        self.to_aws_role_session_name = None

        self._transformations = [lambda x: x]

        self._jobs = []

    def run(self, number_of_images=None, repositories=None):

        from_registry = Registry(
            self._from_registry_id,
            profile_name=self.from_aws_profile,
            region_name=self.from_aws_region,
            role_arn=self.from_aws_role_arn,
            role_session_name=self.from_aws_role_session_name,
        )

        to_registry = Registry(
            self._to_registry_id,
            profile_name=self.to_aws_profile,
            region_name=self.to_aws_region,
            role_arn=self.to_aws_role_arn,
            role_session_name=self.to_aws_role_session_name
        )

        return self._compare(from_registry, to_registry, number_of_images=number_of_images, repositories=repositories)

    def _compare(self, from_registry, to_registry, number_of_images=None, repositories=None):

        if repositories is not None:
            print(
                f'Sync selected repositories of {to_registry.url} ({len(to_registry.repositories)}) with {from_registry.url} ({len(from_registry.repositories)})')
            print(colored(f'Selected: {", ".join(repositories.keys())}', 'blue'))
        else:
            print(
                f'Sync all matching repositories of {to_registry.url} ({len(to_registry.repositories)}) with {from_registry.url} ({len(from_registry.repositories)})')

        found = {}
        skipped = []
        not_found = []

        for repository in to_registry.repositories:

            for transformation in self.transformations:

                result = from_registry.includes(
                    repository,
                    ignore_namespace=True,
                    transformation=transformation,
                    repositories=repositories.keys() if repositories != None else None
                )

                if result:

                    repository_spec = None

                    if repositories is not None:
                        repository_spec = repositories[result.name(ignore_namespace=True)]

                        if 'limit' in repository_spec:
                            number_of_images = repository_spec['limit']

                        if 'versions' in repository_spec:
                            versions = repository_spec['versions']
                        else:
                            versions = None

                    images = result.images(number_of_images=number_of_images, versions=versions)

                    found[repository.name()] = {
                        'name': result.name(),
                        'name_without_namespace': result.name(ignore_namespace=True),
                        'tags': [image.tag for image in images]
                    }

                    for image in images:
                        job = Job(
                            source_registry=from_registry.url,
                            source_username=from_registry.username,
                            source_password=from_registry.password,
                            target_registry=to_registry.url,
                            target_username=to_registry.username,
                            target_password=to_registry.password,
                            source_repository=f'{from_registry.name}/{result.name()}',
                            source_image_tag=f'{image.tag}',
                            source_image_url=f'{image.url}',
                            target_repository=f'{to_registry.name}/{repository.name()}',
                            target_image_tag=image.tag,
                            target_image_url=f'{to_registry.name}/{repository.name()}:{image.tag}'
                        )
                        self._jobs.append(job)

                    break

            if result is None:
                if repositories is None:
                    not_found.append(repository.name())
                else:
                    skipped.append(repository.name())

        # Check if the included repos have been found
        if repositories is not None:
            for repository in repositories:
                if repository not in [value["name_without_namespace"] for key, value in found.items()]:
                    not_found.append(repository)

        for repo, result in found.items():
            print(
                colored(f'{repo}', 'green'),
                f'is found as',
                colored(f'{result["name"]}.', 'yellow')
            )

        for repo in skipped:
            print(
                colored(f'{repo}.', 'blue'),
                'skipped.'
            )

        for repo in not_found:
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
