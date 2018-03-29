import unittest

import cfg
from implementation.app_constants import *
from implementation.downloader import Downloader
from implementation.parser import FileParser
from settings import get_cmdline_args
from .helper import Helper


class DownloaderTestCase ( unittest.TestCase ):
    def setUp ( self ):
        """
        Method called before any unittest case
        :return:
        """
        self.file_descriptor = get_cmdline_args ( [ "--file", "./implementation/unittest/mock_image_urls.txt" ] )

        # starting file parser
        self.parser = FileParser ( self.file_descriptor )
        self.parser.start_parser_thread ( )
        # waiting for file parser thread (Normally it will finish first)
        self.parser.wait_for_parser_thread ( )

        self.helper = Helper ( parser=self.parser )
        self.helper.create_default_cfg ( )

        self.url_dl = Downloader ( self.parser.url_queue )
        self.helper.stop_downloader_threads ( self.url_dl.dl_thread_list )

    def tearDown ( self ):
        """
        Method called after every unittest case
        :return:
        """
        self.helper.delete_dl_logs ( (cfg.APP_CFG[ IMAGE_SAVE_DIR ], cfg.APP_CFG[ LOG_DIR ]) )

    def test_parser_downloader_system ( self ):
        """
        Test the whole system of FileParser - Downloader. In the end the FileParser.url_queue will have only 1 \
        item left which is "EXIT".

        Please look into the corresponding code in run_parser_downloader.py.
        :return:
        """
        # starting url downloader threads
        self.url_dl.start_downloader_threads ( )

        # waiting for downloader threads
        self.url_dl.wait_for_downloader_threads ( )

        # there will be just 1 entry in FileParser.url_queue queue which is "EXIT"
        self.assertEqual ( self.parser.url_queue.qsize ( ), 1 )

    def test_success_download_image ( self ):
        """
        Verifies that application downloads a valid web address link.
        Please look into corresponding function download_image in downloader.py
        :return:
        """
        dl_status = self.url_dl.download_image (
            "https://www.elegantthemes.com/blog/wp-content/uploads/2015/02/custom-trackable-short-url-feature.png" )
        self.assertTrue ( dl_status )

    def test_failure_download_image ( self ):
        """
        Verifies that application does not download an invalid web address link.
        Please look into corresponding function download_image in downloader.py
        :return:
        """
        dl_status = self.url_dl.download_image ( "mk.com" )
        self.assertFalse ( dl_status )

    def test_thread_downloader ( self ):
        """
        Verifies that application downloads image urls.
        Please look into corresponding function thread_downloader in downloader.py
        :return:
        """
        self.url_dl.thread_downloader ( )

        # there will be just 1 entry in FileParser.url_queue queue which is "EXIT"
        self.assertEqual ( self.parser.url_queue.qsize ( ), 1 )
