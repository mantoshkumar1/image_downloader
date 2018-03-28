import logging
import queue
import threading

import requests

import cfg
from .app_constants import *


class FileParser:
    """
    Description: FileParser class contains methods which collectively work together to parse a document. \
                 This document contains image URLs, one per line. FileParser parses the document and put \
                 the URLs into a queue which is consumed by downloader threads.

    Version: 1.0
    Comment:
    """

    def __init__ ( self, url_fd ):
        self.logger = logging.getLogger ( __name__ )

        # File descriptor to the file containing urls (provided by user through command line argument)
        self.url_fd = url_fd

        # Name to the file containing urls (provided by user through command line argument)
        self.url_fname = self.url_fd.name

        # BOM encoding type (a string) of the plaintext file provided in the argument
        self.encoding = self.detect_bom_markers ( )

        # this queue holds only serviceable urls which are consumed by downloader threads
        # FileParser is the producer of urls in this queue, while Downloader is consumer
        self.url_queue = queue.Queue ( maxsize=50 )

        # file parser thread
        self.parser_thread = threading.Thread ( target=self.parse_image_url_file )

    def detect_bom_markers ( self ):
        '''
        This function detects the encoding of the plaintext file provided in the argument by reading the first 4 bytes of the document.

        Specification Reference: http://unicodebook.readthedocs.io/guess_encoding.html#check-for-bom-markers
        Stackoverflow Reference: https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python

        Return: BOM encoding type (a string)
        '''
        # codecs module provides the constants which are useful for reading and writing to platform dependent files.
        # BOM (Byte Order Mark) is used  to detect the endianness of a UTF-16 or UTF-32 byte sequence and is also \
        # used as a signature to guess the encoding
        import codecs  # used to get defined BOM constants

        BOMS = (
            (codecs.BOM_UTF8, "UTF-8-SIG"),
            (codecs.BOM_UTF32_BE, "UTF-32-BE"),
            (codecs.BOM_UTF32_LE, "UTF-32-LE"),
            (codecs.BOM_UTF16_BE, "UTF-16-BE"),
            (codecs.BOM_UTF16_LE, "UTF-16-LE"),
        )

        data = self.url_fd.read ( 4 )  # reading 4 bytes from the beginning of the file
        for bom, encoding in BOMS:
            if data.startswith ( bom ):
                self.url_fd.close ( )
                self.url_fd = None
                return encoding

        self.url_fd.close ( )
        self.url_fd = None

        # For most plaintext programs, UTF-8 is the default encoding signature which python calls UTF-8-SIG
        # Reference: https://docs.python.org/2/library/codecs.html
        return "UTF-8-SIG"

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

    def start_parser_thread ( self ):
        """
        Starts parser thread
        :return:
        """
        self.parser_thread.start ( )

    def wait_for_parser_thread ( self ):
        """
        Waits for file parser thread
        :return:
        """
        self.parser_thread.join ( )

    def parse_image_url_file ( self ):
        """
        Parse the file that contains url per line and put it into a queue if the url is serviceable.
        :return:
        """
        with open ( file=self.url_fname, mode='r', encoding=self.encoding, newline=None ) as fd:
            for line_terminated in fd:
                # removing newline from line_terminated
                url = line_terminated.rstrip ( '\n' )

                if self.is_url_serviceable ( url ):
                    self.url_queue.put ( item=url, block=True, timeout=None )

        # "EXIT" will be used by downloader threads to terminate themselves
        self.url_queue.put ( item="EXIT", block=True, timeout=None )
