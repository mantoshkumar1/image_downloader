import unittest

import cfg
from implementation.app_constants import *
from implementation.parser import FileParser
from settings import get_cmdline_args
from .helper import Helper


# assert method Reference: https://docs.python.org/3.5/library/unittest.html#assert-methods

class ParserTestCase ( unittest.TestCase ):
    def setUp ( self ):
        """
        Method called before any unittest case
        :return:
        """
        self.helper = Helper ( )

        self.helper.create_default_cfg ( )

        self.file_descriptor = get_cmdline_args ( [ "--file", "./implementation/unittest/mock_image_urls.txt" ] )
        self.parser = FileParser ( self.file_descriptor )

    def tearDown ( self ):
        """
        Method called after every unittest case
        :return:
        """
        self.helper.delete_dl_logs ( (cfg.APP_CFG[ IMAGE_SAVE_DIR ], cfg.APP_CFG[ LOG_DIR ]) )

    def test_file_encoding ( self ):
        """
        It tests how detect_bom_markers detects the used encoding method of mock_image_urls.txt.
        Please look into corresponding function detect_bom_markers in parser.py.
        :return:
        """
        self.assertEqual ( self.parser.encoding, "UTF-8-SIG" )

    def test_url_unserviceable ( self ):
        """
        It tests how is_url_serviceable ignores unserviceable url.
        Please look into corresponding function is_url_serviceable in parser.py
        :return:
        """
        self.assertFalse ( self.parser.is_url_serviceable ( "www.mardwa.com" ) )

    def test_videourl_serviceable ( self ):
        """
        It tests how is_url_serviceable ignores serviceable url which is not of image-type.
        Please look into corresponding function is_url_serviceable in parser.py
        :return:
        """
        self.assertFalse ( self.parser.is_url_serviceable (
            "http://www.sample-videos.com/video/mp4/720/big_buck_bunny_720p_1mb.mp4" ) )

    def test_url_image_serviceable ( self ):
        """
        It tests how is_url_serviceable accepts serviceable image url.
        Please look into corresponding function is_url_serviceable in parser.py
        :return:
        """
        self.assertTrue ( self.parser.is_url_serviceable (
            "https://www.elegantthemes.com/blog/wp-content/uploads/2015/02/custom-trackable-short-url-feature.png" ) )

    def test_parse_image_url_file ( self ):
        """
        It tests the functionality of parse_image_url_file function.
        Please look into corresponding function parse_image_url_file in parser.py
        :return:
        """
        # putting serviceable items in queue
        self.parser.parse_image_url_file ( )

        # there are 2 serviceable urls in mock_image_urls.txt + "EXIT" = 3
        self.assertEqual ( self.parser.url_queue.qsize ( ), self.helper.num_serviceable_urls ( self.parser ) )

    def test_parser_thread ( self ):
        """
        It tests how threads start, parse mock_image_urls.txt and terminates.
        Please look into corresponding function start_parser_thread and wait_for_parser_thread in parser.py
        :return:
        """
        self.parser.start_parser_thread ( )
        self.parser.wait_for_parser_thread ( )

        # there are 2 serviceable urls in mock_image_urls.txt + "EXIT" = 3
        self.assertEqual ( self.parser.url_queue.qsize ( ), self.helper.num_serviceable_urls ( self.parser ) )
