import unittest

from settings import configure_application
from settings import get_cmdline_args
from .helper import Helper


class SettingsTestCase ( unittest.TestCase ):
    def setUp ( self ):
        """
        Method called before any unittest case
        :return:
        """
        self.helper = Helper ( )
        self.cfg = self.helper.create_default_cfg ( )

    def tearDown ( self ):
        """
        Method called after every unittest case
        :return:
        """
        pass

    def test_setting ( self ):
        """
        It creates an cfg.APP_CFG with invalid values and test how default values get enforced by application.
        Please look into corresponding function configure_application in settings.py.
        :return:
        """
        self.cfg = self.helper.create_invalid_cfg ( )

        # application enforces default values for cfg.APP_CFG
        configure_application ( )

        self.assertDictEqual ( self.cfg, self.helper.create_default_cfg ( ) )

    @staticmethod
    def test_valid_cmdline_args ( ):
        """
        It tests how get_cmdline_args accepts valid args
        Please look into corresponding function get_cmdline_args in settings.py.
        :return:
        """
        file_descriptor = get_cmdline_args ( [ "--file", "./implementation/unittest/mock_image_urls.txt" ] )
        file_descriptor.close ( )
        assert file_descriptor

    def test_invalid_cmdline_args ( self ):
        """
        It tests how get_cmdline_args rejects invalid args
        Please look into corresponding function get_cmdline_args in settings.py.
        # Reference: https://stackoverflow.com/questions/129507/how-do-you-test-that-a-python-function-throws-an-exception?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        :return:
        """
        self.assertRaises ( SystemExit, lambda: get_cmdline_args ( [ ] ) )
