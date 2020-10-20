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

    def images(self, number_of_images=None, versions=None):

        name = self.name(ignore_namespace=True)

        if number_of_images is None or number_of_images > 1000:
            max_results = 1000
        else:
            max_results = number_of_images



        if not self._images:

            if versions is not None:

              response = self._registry.client.list_images(
                  repositoryName=self._name,
                  maxResults=max_results,
                  filter={'tagStatus': 'TAGGED'}
              )

              self._images += self._process_response(response)

              if number_of_images is None or number_of_images > max_results:

                  while 'nextToken' in response:
                      print(f'Getting another {max_results}, next {response["nextToken"]}')

                      response = self._registry.client.list_images(
                          repositoryName=self._name,
                          maxResults=max_results,
                          nextToken=response['nextToken'],
                          filter={'tagStatus': 'TAGGED'}
                      )

                      self._images += self._process_response(response)
            else:

              response = self._registry.client.batch_get_image(
                  repositoryName=self._name,
                  imageIds=[{'imageTag': tag} for tag in versions],
                  acceptedMediaTypes=[
                      'string',
                  ]
              )

              self._images += self._process_response({
                "imagesIds": [
                  {'imageTag' : image['imageId']['imageTag']} for image in response['images']
                ]
              })

              # TODO: Improve 
              if len((failures := response['failures'])) > 0:
                print(failures)


        return self._images

    def _process_response(self, response):
        images = []
        for image_id in response["imageIds"]:
            image = Image(self._registry, self, image_id["imageTag"])
            images.append(image)

        return images

    def name(self, ignore_namespace=False):
        return self._name if not ignore_namespace else self._name.split("/")[-1]
