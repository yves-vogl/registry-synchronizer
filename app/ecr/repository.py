#
# Copyright (c) 2020 Yves Vogl
#

from .image import Image

class Repository:

  def __init__(self, registry, name):

    self._images = []
    self._image_urls = None

    self._registry = registry
    self._name = name

  def images(self, number_of_images = 1000):

    if self._images == []:
      for image_id in self._registry.client.list_images(
        repositoryName = self._name,
        maxResults = number_of_images,
        filter = {'tagStatus': 'TAGGED'}
      )["imageIds"]:
        image = Image(self._registry, self, image_id["imageTag"])
        self._images.append(image)

    return self._images

  def name(self, ignore_namespace = False):
    return self._name if not ignore_namespace else self._name.split("/")[-1]
