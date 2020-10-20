#
# Copyright (c) 2020 Yves Vogl
#

class Image:

    def __init__(self, registry, repository, tag):
        self._registry = registry
        self._repository = repository
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    @property
    def name(self):
        return f'{self._repository.name()}:{self._tag}'

    @property
    def url(self):
        return f'{self._registry.name}/{self.name}'
