import logging

from multiprocessing.dummy import Pool as ThreadPool
import requests  # todo: add in setup
from tqdm import tqdm  # todo: add in setup

from threading import Lock

from cfg import APP_CFG as cfg
from .app_constants import *


class ParserDownloader:
    def __init__ ( self ):
        # this will be used if because of any reason function "get_filename_from_url"
        # could not derive a file name
        self.custom_file_id = 0

        # this is used by downloader threads to get a lock over self.custom_file_id
        self.mutex = Lock ( )

        # How to enable logging: https://gist.github.com/wrunk/1241503
        self.logger = logging.getLogger (__name__)

    def verify_cfg_args( self ):
        """
        cfg[MAX_DOWNLOAD_REATTEMPTS] should be >= 0 or None
        cfg[SYSTEM_PROXY] should be either None or empty dict or valid ips in dict
        :return:
        """
        pass

    def is_url_serviceable ( self, url, reattempt_count = cfg[MAX_DOWNLOAD_REATTEMPTS]):
        """
        Verifying whether or not, the url is a downloadable image resource by retrieving meta-information \
        written in response headers, without having to transport the entire content.

        HTTP HEAD is cpu economic for application to verify whether or not, the url is serviceable.

        :param url: string
        :param reattempt_count: integer (Number of reattempts to make if the request times out)
        :return: boolean (If the url is serviceable, it returns True, otherwise False)
        """

        self.logger.critical("critical")
        self.logger.info("Info")

        try:
            response = requests.head (
                url,
                allow_redirects=True,
                stream=False,
                timeout=cfg[URL_TIMEOUT],
                proxies=cfg[SYSTEM_PROXY]
            )

            # Raises stored HTTPError, if one occurred.
            response.raise_for_status ( )


        # Reference: http://docs.python-requests.org/en/master/api/#exceptions
        except requests.exceptions.Timeout as t_err:  # Maybe set up for a retry, or continue in a retry loop
            print (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format (url,
                                                                                              type (t_err).__name__,
                                                                                              t_err.args))

            # if (reattempt_count = 0) or (cfg[MAX_DOWNLOAD_REATTEMPTS] = 0 or None)
            if not reattempt_count: return False
            return self.is_url_serviceable (url, reattempt_count - 1)

        except (requests.exceptions.ConnectionError,  # connection-related errors
                requests.exceptions.HTTPError,  # 401 Unauthorized
                requests.exceptions.URLRequired,  # invalid URL
                requests.exceptions.TooManyRedirects,  # request exceeds the configured number of max redirections
                requests.exceptions.RequestException  # Mother of all requests exceptions. it's doomsday :D
                ) as err:
            print (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format (url, type (err).__name__,
                                                                                              err.args))
            return False

        content_type = response.headers.get ('content-type')
        if not content_type: return False

        if 'image' in content_type.lower ( ):
            return True
        if 'png' in content_type.lower ( ):
            return True

        return False


    def download_image ( self, url, reattempt_count = cfg[MAX_DOWNLOAD_REATTEMPTS] ):
        # Does the url contain a downloadable image resource
        header_res = self.is_url_serviceable (url)
        if not header_res:
            print ("URL: %s may not contain downloadable image resource." % (url))
            return

        # downloading the file now
        # stream=True is set on the request, this avoids reading the content at once into memory for large responses.
        # timeout parameter specifies Requests to stop waiting for a response after a given number of seconds.
        try:
            response = requests.get (
                url,
                allow_redirects=True,
                stream=True,
                timeout=cfg[URL_TIMEOUT],
                proxies=cfg[SYSTEM_PROXY]
            )

            # Raises stored HTTPError, if one occurred.
            response.raise_for_status ( )

        # Reference: http://docs.python-requests.org/en/master/api/#exceptions
        except requests.exceptions.Timeout as t_err:  # Maybe set up for a retry, or continue in a retry loop
            print (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format (url,
                                                                                              type (t_err).__name__,
                                                                                              t_err.args))

            # if (reattempt_count = 0) or (cfg[MAX_DOWNLOAD_REATTEMPTS] = 0 or None)
            if not reattempt_count: return
            self.download_image (url, reattempt_count - 1)
            return

        except (requests.exceptions.ConnectionError,  # connection-related errors
                requests.exceptions.HTTPError,  # 401 Unauthorized
                requests.exceptions.URLRequired,  # invalid URL
                requests.exceptions.TooManyRedirects,  # request exceeds the configured number of max redirections
                requests.exceptions.RequestException  # Mother of all requests exceptions. it's doomsday :D
                ) as err:
            print (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format (url, type (err).__name__,
                                                                                              err.args))
            return

        if response.status_code != 200:
            print ("For URL: %s - Received status code %s. Reason: %s" % (url, response.status_code, response.reason))
            return

        path = cfg[IMAGE_SAVE_DIR] + self.get_filename_from_url (url)

        with open (path, 'wb') as fp:
            # Iterates over the response data. When stream=True is set on the request, this avoids \
            # reading the content at once into memory for large responses. The chunk size is the \
            # number of bytes it should read into memory.
            chunk_size = 1024
            for data_block in tqdm (response.iter_content (chunk_size)):
                fp.write (data_block)

        return

    def does_file_exist ( self, file_path ):
        # todo: put in parser dir
        pass

    def get_filename_from_url ( self, url ):
        """
        # todo: put in parser dir
        Get filename from url
        :param url: string
        :return: file_name: string (e.g; "/application_image_1.png" or "/tiger_image.png")
        """

        def create_file_name ( ):
            self.mutex.acquire ( )
            curr_file_id = self.custom_file_id
            self.custom_file_id += 1
            self.mutex.release ( )

            file_name = "/application_image_" + str (curr_file_id) + ".png"
            return file_name

        # todo: I think I will already url before?
        # if not url: return create_file_name()

        file_name = url.split ("/")[-1]
        if not file_name: return create_file_name ( )

        return "/" + file_name
