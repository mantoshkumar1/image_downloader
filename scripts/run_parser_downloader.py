#!/usr/bin/python3
from implementation.downloader import Downloader
from implementation.parser import FileParser
from settings import configure_application, get_cmdline_args

# configuring application using defined configurations
configure_application ( )

# Asking user from command line argument for plaintext file path
url_fd = get_cmdline_args ( )

# starting file parser
fp = FileParser ( url_fd )
fp.start_parser_thread ( )

# starting url downloader threads
url_dl = Downloader ( fp.url_queue )
url_dl.start_downloader_threads ( )

# waiting for file parser thread (Normally it will finish first)
fp.wait_for_parser_thread ( )

# waiting for downloader threads
url_dl.wait_for_downloader_threads ( )

print ( "----------------------------------------------------" )
print ( "<<Thank you for using image downloader application>>" )
print ( "----------------------------------------------------" )
