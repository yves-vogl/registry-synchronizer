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

  def images(self, number_of_images = None, versions = None):

    name = self.name(ignore_namespace = True)

    if versions != None and name in versions:
      version_spec = versions[name]

    if number_of_images == None or number_of_images > 1000:
      max_results = 1000
    else:
      max_results = number_of_images

    if self._images == []:

      response = self._registry.client.list_images(
        repositoryName = self._name,
        maxResults = max_results,
        filter = {'tagStatus': 'TAGGED'}
      )

      self._images += self._process_response(response)

      if number_of_images == None or number_of_images > max_results:

        while 'nextToken' in response:

          print(f'Getting another {max_results}, next {response["nextToken"]}')

          response = self._registry.client.list_images(
            repositoryName = self._name,
            maxResults = max_results,
            nextToken = response['nextToken'],
            filter = {'tagStatus': 'TAGGED'}
          )

          self._images += self._process_response(response)


    return self._images


  def _process_response(self, response):
    images = []
    for image_id in response["imageIds"]:
      image = Image(self._registry, self, image_id["imageTag"])
      images.append(image)

    return images


  def name(self, ignore_namespace = False):
    return self._name if not ignore_namespace else self._name.split("/")[-1]
