from multiprocessing.dummy import Pool as ThreadPool
import requests
from threading import Lock

from cfg import APP_CFG
from .app_constants import *

class ParserDownloader:
    def __init__ ( self ):
        # this will be used if because of any reason function "get_filename_from_url"
        # could not derive a file name
        self.custom_file_id = 0

        # this is used by downloader threads to get a lock over self.custom_file_id
        self.mutex = Lock ( )

    def is_url_downloadable ( self, url ):
        """
        Does the url contain a downloadable image resource
        It is cpu economic to verify whether the url is downloadable or not by just fetching
        the response header.
        :param url: string
        :return: boolean
        """
        h = requests.head (url, allow_redirects=True)
        header = h.headers
        content_type = header.get ('content-type')
        if 'image' in content_type.lower ( ):
            return True
        if 'png' in content_type.lower():
            return True

        return False

    def download_image( self, url ):
        header_res = self.is_url_downloadable(url)
        if not header_res: return

        # downloading the file now
        # stream=True is set on the request, this avoids reading the content at once into memory for large responses.
        response = requests.get(url, allow_redirects=True, stream=True)

        path = APP_CFG[IMAGE_SAVE_DIR] + self.get_filename_from_url (url)

        if response.status_code == 200:
            with open (path, 'wb') as f:
                for block in response.iter_content (1024):
                    f.write (block)

    def get_filename_from_url ( self, url ):
        """
        Get filename from url
        :param url: string
        :return: file_name: string
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
