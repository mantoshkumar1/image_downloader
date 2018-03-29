import logging
import logging.config

import cfg
from implementation.app_constants import *

logger = logging.getLogger ( __name__ )


def set_log_level ( ):
    """
    This function set the log level of this application using "LOG_LEVEL" defined in cfg.py.
    In case of invalid LOG_LEVEL configuration, it enables INFO level of logging.
    :return:
    """
    # Reference: https://docs.python.org/2/howto/logging.html#logging-levels
    std_logging_levels = {
        "NOTSET": logging.NOTSET,  # lowest priority
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,  # highest priority
    }

    cfg_log_level = cfg.APP_CFG.get ( LOG_LEVEL )
    if not cfg_log_level:
        logger.info ( "{0}: {1}".format ( "Warning", "LOG_LEVEL is not configured in cfg.py. " +
                                          "Logging is configured to INFO level by default." ) )
        cfg_log_level = "INFO"

    mapped_log_level = std_logging_levels.get ( cfg_log_level.upper ( ) )

    # if an invalid option is configured in cfg, set logger to "INFO"
    if not mapped_log_level:
        logger.info ( "{0}: {1}".format ( "Warning", "LOG_LEVEL is not configured as specified in cfg.py. " +
                                          "Logging is configured to INFO level by default." ) )

        cfg_log_level = "INFO"
        mapped_log_level = std_logging_levels[ "INFO" ]

    cfg.APP_CFG[ LOG_LEVEL ] = cfg_log_level
    logging.getLogger ( ).setLevel ( mapped_log_level )


def configure_logging ( ):
    """
    Configures logging using predefined default configuration in ".logging.conf"
    :return:
    """
    log_file_path = cfg.APP_CFG[ LOG_DIR ] + "/app.log"
    logging.config.fileConfig (
        fname='.logging.conf',
        defaults={'logfilename': log_file_path},
        disable_existing_loggers=False
    )


def verify_cfg ( ):
    """
    Verify the configuration of the application present in cfg.py.
    This function attempts to fix the config issues, provide warning message to user and in case
    of critical error, it exits the program.
    :return:
    """
    from collections import defaultdict
    import os

    error_msg_dict = defaultdict ( lambda: [ ] )

    # verification of IMAGE_SAVE_DIR
    image_save_dir = cfg.APP_CFG.get ( IMAGE_SAVE_DIR )
    if not image_save_dir:
        error_msg_dict[ "Warning" ].append (
            "IMAGE_SAVE_DIR is not configured in cfg.py. Default configuration is activated with ./downloaded_images." )
        cfg.APP_CFG[ IMAGE_SAVE_DIR ] = './downloaded_images'

    try:
        os.makedirs ( image_save_dir, exist_ok=True )
    except PermissionError:
        error_msg_dict[ "Critical" ].append (
            "User has no permission to the configured IMAGE_SAVE_DIR. " +
            "Default configuration is activated with ./downloaded_images." )
        cfg.APP_CFG[ IMAGE_SAVE_DIR ] = './downloaded_images'

    # verification of URL_TIMEOUT
    try:
        url_timeout = cfg.APP_CFG[ URL_TIMEOUT ]
        if url_timeout and url_timeout < 0:
            error_msg_dict[ "Warning" ].append (
                "URL_TIMEOUT is negative in cfg.py. Default configuration of 2 seconds is activated." )
            cfg.APP_CFG[ URL_TIMEOUT ] = 2
    except KeyError:
        error_msg_dict[ "Warning" ].append (
            "URL_TIMEOUT is not configured in cfg.py. Default configuration of 2 seconds is activated." )
        cfg.APP_CFG[ URL_TIMEOUT ] = 2

    # verification of MAX_DOWNLOAD_REATTEMPTS
    # If URL_TIMEOUT is already set to None, then MAX_DOWNLOAD_REATTEMPTS will never be used anyway
    if cfg.APP_CFG[ URL_TIMEOUT ]:
        max_dwld_attempts = cfg.APP_CFG.get ( MAX_DOWNLOAD_REATTEMPTS )
        if max_dwld_attempts is None or max_dwld_attempts < 0:
            error_msg_dict[ "Info" ].append (
                "By default MAX_DOWNLOAD_REATTEMPTS has been configured to 0, as provided value is " +
                "either None or negative or not provided." )

            cfg.APP_CFG[ MAX_DOWNLOAD_REATTEMPTS ] = 0

    # verification of SYSTEM_PROXY
    try:
        sys_proxy = cfg.APP_CFG[ SYSTEM_PROXY ]
        if sys_proxy is not None and type ( sys_proxy ) is not dict:
            error_msg_dict[ "Warning" ].append (
                "SYSTEM_PROXY should have been a dict. By default configuring it to None. " +
                "Connection might fail due to wrong proxy configuration." )
            cfg.APP_CFG[ SYSTEM_PROXY ] = None

    except KeyError:
        error_msg_dict[ "Warning" ].append (
            "SYSTEM_PROXY is not configured in cfg.py. By default application configures it " +
            "to None. Connection might fail due to wrong proxy configuration." )
        cfg.APP_CFG[ SYSTEM_PROXY ] = None

    # verification of LOG_DIR
    log_dir = cfg.APP_CFG.get ( LOG_DIR )
    if not log_dir:
        error_msg_dict[ "Warning" ].append (
            "LOG_DIR is not configured in cfg.py. Default configuration is activated with ./logs." )
        cfg.APP_CFG[ LOG_DIR ] = './logs'

    try:
        os.makedirs ( log_dir, exist_ok=True )
    except PermissionError:
        error_msg_dict[ "Critical" ].append (
            "User has no permission to the configured LOG_DIR. Default configuration is activated with ./logs." )
        cfg.APP_CFG[ LOG_DIR ] = './logs'

    # verification of LOG_LEVEL
    # This is verified in set_log_level function

    # printing error msg on console
    for error_severity in error_msg_dict:
        error_msg_list = error_msg_dict[ error_severity ]
        for msg in error_msg_list:
            logger.info ( "{0}: {1}".format ( error_severity, msg ) )


def configure_application ( ):
    """
    This function configures the application and logging setup and verifies the user configuration defined in cfg.py.
    :return:
    """
    verify_cfg ( )

    configure_logging ( )
    set_log_level ( )


def get_cmdline_args ( test_args=[ ] ):
    """
    Takes the file path of plaintext file as an argument which contains image URLs through command line arguments \
    from user and returns the file descriptor.
    :param test_args: only used for testing argparse  capabilty to parse command-line arguments
    :return: file descriptor of the plaintext file
    """
    import argparse
    parser = argparse.ArgumentParser ( description='File Parser - Web Image Downloader' )
    required = parser.add_argument_group ( 'required arguments' )
    required.add_argument ( '-f', '--file', dest='infile', required=True, metavar="FILE_PATH",
                            type=argparse.FileType ( 'rb' ),
                            help='Relative/Absolute path to the file that contains urls' )

    if test_args:
        args = parser.parse_args ( test_args )
    else:
        args = parser.parse_args ( )

    return args.infile
