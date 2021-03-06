import cfg
from implementation.app_constants import *


class Helper:
    def __init__ ( self, parser=None ):
        self.parser = parser

    @staticmethod
    def create_cfg ( image_save_dir=None,
                     url_timeout=None,
                     max_dl_attempt=None,
                     sys_proxy=None,
                     log_dir=None,
                     log_lvl=None ):
        """
        Create a new cfg.APP_CFG. Please look into cfg.py for details.
        :param image_save_dir: IMAGE_SAVE_DIR
        :param url_timeout: URL_TIMEOUT
        :param max_dl_attempt: MAX_DOWNLOAD_REATTEMPTS
        :param sys_proxy: SYSTEM_PROXY
        :param log_dir: LOG_DIR
        :param log_lvl: LOG_LEVEL
        :return: A new cfg.APP_CFG
        """
        new_cfg = cfg.APP_CFG
        new_cfg[ IMAGE_SAVE_DIR ] = image_save_dir
        new_cfg[ URL_TIMEOUT ] = url_timeout
        new_cfg[ MAX_DOWNLOAD_REATTEMPTS ] = max_dl_attempt
        new_cfg[ SYSTEM_PROXY ] = sys_proxy
        new_cfg[ LOG_DIR ] = log_dir
        new_cfg[ LOG_LEVEL ] = log_lvl

        return new_cfg

    def create_default_cfg ( self ):
        """
        Create a new cfg.APP_CFG with default valid values. Please look into cfg.py for details.
        :return: A new cfg.APP_CFG
        """
        new_cfg = self.create_cfg (
            image_save_dir="./downloaded_images",
            url_timeout=2,
            max_dl_attempt=2,
            sys_proxy=None,
            log_dir="./logs",
            log_lvl="info"
        )

        return new_cfg

    def create_invalid_cfg ( self ):
        """
        Create a new cfg.APP_CFG with valid values. Please look into cfg.py for details.
        :return: A new invalid cfg.APP_CFG
        """
        new_cfg = self.create_cfg (
            image_save_dir="/mantosh_downloaded",
            url_timeout=-1,
            max_dl_attempt=-1,
            sys_proxy=(),
            log_dir="/mantosh_logs",
            log_lvl="invalid"
        )

        return new_cfg

    @staticmethod
    def delete_dl_logs ( del_dirs_tup ):
        """
        Delete all the contents within Download and Log directory which is generated by unittest
        :param del_dirs_tup: a tuple which contains download_dir and log_dir of the application
        :return:
        """
        import os
        for del_dir in del_dirs_tup:
            file_list = os.listdir ( del_dir )
            for fileName in file_list:
                os.remove ( del_dir + "/" + fileName )

    @staticmethod
    def num_serviceable_urls ( parser ):
        """
        Please look into corresponding function is_url_serviceable in parser.py
        :param parser: Parset Object
        :return: number of serviceable urls in mock_image_urls.txt + 1 [1 is added for "EXIT"]
        """
        file_name = parser.url_fname
        count = 0
        with open ( file=file_name, mode='r', encoding=parser.encoding, newline=None ) as fd:
            for line_terminated in fd:
                # removing newline from line_terminated
                url = line_terminated.rstrip ( '\n' )

                if parser.is_url_serviceable ( url ):
                    count += 1

        # adding 1 for "EXIT"
        count += 1

        return count

    @staticmethod
    def stop_downloader_threads ( th_list ):
        """
        This function stops the downloader threads explicitly.
        Reference: http://www.xavierdupre.fr/blog/2013-11-02_nojs.html
        :param th_list:
        :return:
        """
        for th in th_list:
            th._stop ( )
