import logging
import requests
import queue
import threading
import cfg
from .app_constants import *


class FileParser:
    def __init__ ( self ):
        self.logger = logging.getLogger ( __name__ )

        # this queue holds only serviceable urls which are consumed by downloader threads
        self.url_queue = queue.Queue ( maxsize=50 )

        # file parser thread
        self.parser_thread = threading.Thread(target=self.parse_image_url_file)

    def is_url_serviceable ( self, url, reattempt_count=cfg.APP_CFG.get ( MAX_DOWNLOAD_REATTEMPTS ) ):
        """
        Verifying whether or not, the url is a downloadable image resource by retrieving meta-information \
        written in response headers, without having to transport the entire content.

        HTTP HEAD is cpu economic for application to verify whether or not, the url is serviceable.

        :param url: string
        :param reattempt_count: integer (Number of reattempts to make if the request times out)
        :return: boolean (If the url is serviceable, it returns True, otherwise False)
        """
        try:
            response = requests.head (
                url,
                allow_redirects=True,
                stream=False,
                timeout=cfg.APP_CFG[ URL_TIMEOUT ],
                proxies=cfg.APP_CFG[ SYSTEM_PROXY ]
            )

            # Raises stored HTTPError, if one occurred.
            response.raise_for_status ( )


        # Reference: http://docs.python-requests.org/en/master/api/#exceptions
        except requests.exceptions.Timeout as t_err:  # Maybe set up for a retry, or continue in a retry loop
            self.logger.info (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format ( url,
                                                                                               type ( t_err ).__name__,
                                                                                               t_err.args ) )

            if not reattempt_count:
                self.logger.debug ( "URL {} has not been downloaded.".format ( url ) )
                return False

            return self.is_url_serviceable ( url, reattempt_count - 1 )

        except (requests.exceptions.ConnectionError,  # connection-related errors
                requests.exceptions.HTTPError,  # 401 Unauthorized
                requests.exceptions.URLRequired,  # invalid URL
                requests.exceptions.TooManyRedirects,  # request exceeds the configured number of max redirections
                requests.exceptions.RequestException  # Mother of all requests exceptions. it's doomsday :D
                ) as err:
            self.logger.info (
                "For URL: {0} - An exception of type {1} occurred. Arguments:\n{2!r}".format ( url,
                                                                                               type ( err ).__name__,
                                                                                               err.args ) )

            self.logger.debug ( "URL {} is not serviceable.".format ( url ) )
            return False

        content_type = response.headers.get ( 'content-type' )
        if not content_type: return False

        # Verify download resource is an image
        if 'image' in content_type.lower ( ):
            return True
        if 'png' in content_type.lower ( ):
            return True

        self.logger.debug ( "URL {} is not serviceable.".format ( url ) )
        return False

    def start_parser_thread( self ):
        """
        Starts parser thread
        :return:
        """
        self.parser_thread.start()

    def wait_for_parser_thread( self ):
        """
        Waits for file parser thread
        :return:
        """
        self.parser_thread.join()

    def parse_image_url_file ( self ):
        """
        Parse the file that contains url per line and put it into a queue if the url is serviceable.
        :return:
        """
        # It is already verified in verify_cfg function that IMAGE_URLS_FILE_PATH does exist.
        with open ( cfg.APP_CFG[ IMAGE_URLS_FILE_PATH ] ) as fd:
            for line_terminated in fd:
                # removing newline from line_terminated
                url = line_terminated.rstrip ( '\n' )

                if self.is_url_serviceable ( url ):
                    self.url_queue.put ( item=url, block=True, timeout=None )

        # "EXIT" will be used by downloader threads to terminate themselves
        self.url_queue.put(item="EXIT", block=True, timeout=None)
