import logging
import os
import requests
from tqdm import tqdm
import threading

import cfg
from .app_constants import *


class Downloader:
    """
    Description: Downloader class contains methods which collectively work together to download image resources \
                 from urls and save them into user specified system path. As per its mechanism, it employs four \
                 threads to concurrently download the resources. These threads (Consumers) pick up urls from the "url_queue" \
                 which is filled up by FileParser class (Producer).

    Version: 1.0
    Comment:
    """
    def __init__ ( self, url_queue ):
        self.logger = logging.getLogger ( __name__ )

        # contains only serviceable urls in a queue
        # FileParser is the producer of urls in this queue, while Downloader is consumer
        self.url_queue = url_queue

        # this will be used, if because of any reason function "get_filename_from_url"
        # could not derive a file name
        self.custom_file_id = 0

        # default image extension in case downloading file is missing (for non-linux systems)
        self.default_image_ext = "jfif"

        # this is used by downloader threads to get a lock over self.custom_file_id
        self.mutex = threading.Lock ( )

        # Number of downloader threads
        self.NUM_DL_THREADS = 4

        # thread_list contains downloader thread instance which are created and \
        # started by create_start_downloader_threads function
        self.dl_thread_list = [ ]
        self.create_downloader_threads ( )

    def create_downloader_threads ( self ):
        """
        Creates the downloader threads
        :return:
        """
        for _ in range ( self.NUM_DL_THREADS ):
            dwnld_th_inst = threading.Thread ( target=self.thread_downloader )
            self.dl_thread_list.append ( dwnld_th_inst )

    def start_downloader_threads ( self ):
        """
        Starts the downloader threads
        :return:
        """
        for i in range ( self.NUM_DL_THREADS ):
            self.dl_thread_list[ i ].start ( )

    def wait_for_downloader_threads ( self ):
        """
        Waits for and releases resources held by downloader threads
        :return:
        """
        for i in range ( self.NUM_DL_THREADS ):
            self.dl_thread_list[ i ].join ( )

        # Last message for user
        print ( "Download dir is {}".format ( cfg.APP_CFG[ IMAGE_SAVE_DIR ] ) )
        print ( "Log dir is {}".format ( cfg.APP_CFG[ LOG_DIR ] ) )

    def thread_downloader ( self ):
        """
        This function details the functionality of a downloader thread. Each thread fetches items \
        from self.url_queue and download the image resources.
        :return:
        """
        while (True):
            url = self.url_queue.get ( block=True, timeout=None )

            # exit point of a thread (Use "EXIT" to exit and then put it back for other threads to use (and exit)
            if url == "EXIT":
                self.url_queue.put ( item="EXIT", block=True, timeout=None )
                break

            self.download_image ( url )

    def download_image ( self, url, reattempt_count=cfg.APP_CFG.get ( MAX_DOWNLOAD_REATTEMPTS ) ):
        """
        This function downloads image resource from web and saves it into IMAGE_SAVE_DIR directory
        :param url: str
        :param reattempt_count: int (Number of times an url will attempted to be fetched in case of failure)
        :return:
        """
        # stream=True is set on the request, this avoids reading the content at once into memory for large responses.
        # timeout parameter specifies Requests to stop waiting for a response after a given number of seconds.
        try:
            response = requests.get (
                url,
                allow_redirects=True,
                stream=True,
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
                return

            self.download_image ( url, reattempt_count - 1 )
            return

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

            self.logger.debug ( "URL {} has not been downloaded.".format ( url ) )
            return

        if response.status_code != 200:
            self.logger.debug (
                "For URL: %s - Received status code %s. Reason: %s" % (url, response.status_code, response.reason) )
            return

        path = cfg.APP_CFG[ IMAGE_SAVE_DIR ] + self.get_filename_from_url ( url )

        # It is strongly recommended that we open files in binary mode as per requests documentation
        # Reference: http://docs.python-requests.org/en/master/user/quickstart/
        with open ( path, 'wb' ) as fp:
            # Iterates over the response data. When stream=True is set on the request, this avoids \
            # reading the content at once into memory for large responses. The chunk size is the \
            # number of bytes it should read into memory.
            # iter_content automatically decodes the gzip and deflate transfer-encodings.
            chunk_size = 1024
            for data_block in tqdm ( response.iter_content ( chunk_size ) ):
                fp.write ( data_block )

        return

    def create_custom_file_name ( self ):
        """
        Create a customized name for a downloading image file. It is a thread safe function.
        :return: str
        """
        self.mutex.acquire ( )

        curr_file_id = self.custom_file_id
        self.custom_file_id += 1

        self.mutex.release ( )

        custom_file_name = "application_image_" + str ( curr_file_id ) + "." + self.default_image_ext
        return custom_file_name

    def check_create_dup_download_file_name ( self, file_name ):
        """
        Checks whether the file already exist or not in IMAGE_SAVE_DIR directory. \
        If it does not exist, then return the same file_name.
        If it already exist, then returns a customized file_name for this image.

        :param file_name: Name of the downloading image file (str)
        :return: unique file_name of the downloading image into IMAGE_SAVE_DIR directory (str)
        """
        file_path = cfg.APP_CFG[ IMAGE_SAVE_DIR ] + "/" + file_name
        if not os.path.isfile ( file_path ): return file_name

        return self.create_custom_file_name ( )

    def get_filename_from_url ( self, url ):
        """
        Finds filename from url. If it is not possible to get a file name from url then it assigns one.
        :param url: string
        :return: file_name: string (e.g; "/application_image_1.jfif" or "/tiger_image.jfif")
        """
        # striping rightmost '/' char in url if it exists
        url = url.rstrip ( '/' )
        file_name = url.split ( "/" )[ -1 ]

        if not file_name:
            file_name = self.create_custom_file_name ( )

        # web image might lack extension. so verifying and if it lacks ext then assigning one
        file_name_ext = file_name.rsplit ( '.', 1 )
        file_extension = file_name_ext[ -1 ]

        # Available image file formats: http://preservationtutorial.library.cornell.edu/presentation/table7-1.html
        if file_extension not in ("tif", "tiff", "gif", "jpeg", "jpg", "jif", "jfif", "jp2", "jpx", "j2k", "j2c", "fpx", "pcd", "png"):
            # assigning default image extension
            file_extension = self.default_image_ext

        file_name = file_name_ext[0]  + "." + file_extension

        file_name = self.check_create_dup_download_file_name ( file_name )
        return "/" + file_name
