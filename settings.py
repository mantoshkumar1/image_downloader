import logging.config
import logging
import cfg
from implementation.app_constants import *


def set_log_level ( ):
    """
    This function set the log level of this application using "LOG_LEVEL" defined in cfg.py.
    In case of invalid LOG_LEVEL configuration, it enables INFO level of logging.
    :return:
    """
    # Reference: https://docs.python.org/2/howto/logging.html#logging-levels
    std_logging_levels = {
        "NOTSET": logging.NOTSET, # lowest priority
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL, # highest priority
    }

    cfg_log_level = cfg.APP_CFG.get ( LOG_LEVEL )
    if not cfg_log_level:
        print ( "{0}: {1}".format ( "Warning", "LOG_LEVEL is not configured in cfg.py. " + \
                                    "Logging is configured to INFO level by default." ) )
        cfg_log_level = "INFO"

    mapped_log_level = std_logging_levels.get ( cfg_log_level.upper ( ) )

    # if an invalid option is configured in cfg, set logger to "INFO"
    if not mapped_log_level:
        print ( "{0}: {1}".format ( "Warning", "LOG_LEVEL is not configured as specified in cfg.py. " + \
                                    "Logging is configured to INFO level by default." ) )

        cfg_log_level = "INFO"
        mapped_log_level = std_logging_levels[ "INFO" ]

    cfg.APP_CFG[ LOG_LEVEL ] = cfg_log_level
    logging.getLogger ( ).setLevel ( mapped_log_level )


def set_pythonpath ( ):
    """
    This function set the PYTHONPATH for the application.
    :return:
    """
    import sys, os
    try:
        sys.path.index ( os.getcwd ( ) )
    except ValueError:
        sys.path.insert ( 0, os.getcwd ( ) )


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

    error_msg_dict = defaultdict ( lambda: [ ] )
    critical_error_status = False

    # verification of IMAGE_URLS_FILE_PATH
    url_file_path = cfg.APP_CFG.get ( IMAGE_URLS_FILE_PATH )
    if not url_file_path:
        critical_error_status = True
        error_msg_dict[ "Critical" ].append ( "IMAGE_URLS_FILE_PATH must be configured in cfg.py." )

    # verify image url path exists
    import os.path
    if url_file_path and not os.path.isfile ( url_file_path ):
        critical_error_status = True
        error_msg_dict[ "Critical" ].append ( "File name provided at IMAGE_URLS_FILE_PATH does not exist on disk." )

    # verification of IMAGE_SAVE_DIR
    image_save_dir = cfg.APP_CFG.get ( IMAGE_SAVE_DIR )
    if not image_save_dir:
        error_msg_dict[ "Warning" ].append (
            "IMAGE_SAVE_DIR is not configured in cfg.py. Default configuration is activated with ./downloaded_images." )
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
                "By default MAX_DOWNLOAD_REATTEMPTS has been configured to 0, as provided value is " + \
                "either None or negative or not provided." )

            cfg.APP_CFG[ MAX_DOWNLOAD_REATTEMPTS ] = 0

    # verification of SYSTEM_PROXY
    try:
        sys_proxy = cfg.APP_CFG[ SYSTEM_PROXY ]
        if sys_proxy is not None and type ( sys_proxy ) is not dict:
            error_msg_dict[ "Warning" ].append (
                "SYSTEM_PROXY should have been a dict. By default configuring it to None. " + \
                "Connection might fail due to wrong proxy configuartion." )
            cfg.APP_CFG[ SYSTEM_PROXY ] = None

    except KeyError:
        error_msg_dict[ "Warning" ].append (
            "SYSTEM_PROXY is not configured in cfg.py. By default application configures it " + \
            "to None. Connection might fail due to wrong proxy configuartion." )
        cfg.APP_CFG[ SYSTEM_PROXY ] = None

    # verification of LOG_DIR
    log_dir = cfg.APP_CFG.get ( LOG_DIR )
    if not log_dir:
        error_msg_dict[ "Warning" ].append (
            "LOG_DIR is not configured in cfg.py. Default configuration is activated with ./logs." )
        cfg.APP_CFG[ LOG_DIR ] = './logs'

    # verification of LOG_LEVEL
    # This is verified in set_log_level function

    # printing error msg on console
    for error_severity in error_msg_dict:
        error_msg_list = error_msg_dict[ error_severity ]
        for msg in error_msg_list:
            print ( "{0}: {1}".format ( error_severity, msg ) )

    if critical_error_status:  # exit program
        raise SystemExit


def configure_application ( ):
    """
    This function configures the application and logging setup and verifies the \
    user configuration defined in cfg.py.
    :return:
    """
    set_pythonpath ( )
    verify_cfg ( )
    configure_logging ( )
    set_log_level ( )
