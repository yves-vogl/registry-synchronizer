#
# Copyright (c) 2020 Yves Vogl
#

import threading
import docker
from termcolor import colored
from hurry.filesize import size
import sys
import urllib3
import socket


class Job:
    def __init__(self, **kwargs):
        self.target_password = None
        self.target_username = None
        self.target_image_tag = None
        self.target_repository = None
        self.target_image_url = None
        self.source_password = None
        self.source_username = None
        self.source_image_tag = None
        self.source_repository = None
        self.source_image_url = None
        self.__dict__.update(kwargs)

    def log(self, message):
        print(f'{threading.current_thread().ident}: {message}')

    def run(self):
        try:

            client = docker.from_env()

            self.log(f'Pulling {colored(self.source_image_url, "yellow")}')

            image = client.images.pull(
                self.source_repository,
                tag=self.source_image_tag,
                auth_config={
                    'username': self.source_username,
                    'password': self.source_password
                }
            )

            self.log(f'Tagging with {colored(self.target_image_url, "green")}')

            image.tag(
                self.target_repository,
                tag=self.target_image_tag,
            )

            for line in client.images.push(
                    self.target_repository,
                    tag=self.target_image_tag,
                    auth_config={
                        'username': self.target_username,
                        'password': self.target_password
                    },
                    stream=True,
                    decode=True
            ):
                if 'id' in line:
                    if 'total' in line['progressDetail']:

                        current = line["progressDetail"]["current"]
                        total = line["progressDetail"]["total"]

                        if (remaining := total - current) < 0:
                            remaining = 0

                        if (percent := round(current / (total / 100), 1)) > 100.0:
                            percent = 100

                        self.log(
                            f'{line["status"]} {line["id"]}: {percent}% {size(remaining)}'
                        )

                    else:
                        self.log(
                            f'{line["status"]} {line["id"]}'
                        )
                elif 'status' in line:
                    self.log(
                        f'{line["status"]}'
                    )
                else:
                    # 123145559949312: {'progressDetail': {}, 'aux': {'Tag': '0.1.0.957-2f543f5', 'Digest': 'sha256:dcf595bee39bcee215db07aac082770b1f1867851ac8732a8347f9e2f344151c', 'Size': 3058}}
                    self.log(
                        f'{line}'
                    )

            return True

        except docker.errors.APIError as error:
            self.log(colored(error, 'red'))
        except socket.timeout as error:
            self.log(colored(error, 'red'))
        except OSError as error:
            self.log(colored(error, 'red'))
        except urllib3.exceptions.ReadTimeoutError as error:
            self.log(colored(error, 'red'))
        except:
            self.log(colored(f'Unexpected error: {sys.exc_info()[0]})', 'red'))
            raise
        # TODO: Do a configurable retry on socket errors, e.g. on UnixHTTPConnectionPool(host='localhost', port=None): Read timed out.
        # This happens if you have more than 1 thread trying to push or pull from docker.

        finally:
            pass

    def __call__(self):
        self.run()
