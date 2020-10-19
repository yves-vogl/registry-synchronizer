#
# Copyright (c) 2020 Yves Vogl
#

from .image import Image

class Repository:

  def __init__(self, registry, name, max_results = 5):

    self._images = []
    self._image_urls = None

    self._registry = registry
    self._name = name

  @property
  def images(self):

    if self._images == []:
      for image_id in self._registry.client.list_images(
        repositoryName = self._name,
        maxResults = max_results,
        filter = {'tagStatus': 'TAGGED'}
      )["imageIds"]:
        image = Image(self._registry, self, image_id["imageTag"])
        self._images.append(image)

    return self._images

  def name(self, ignore_namespace = False):
    return self._name if not ignore_namespace else self._name.split("/")[-1]
