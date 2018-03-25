import logging.config
logging.config.fileConfig (fname='.logging.conf', disable_existing_loggers=False)

import os, sys
# exporting PYTHONPATH
try:
    # Making it easy for python to find the PYTHONPATH
    sys.path.index(os.getcwd())
except ValueError:
    sys.path.insert(0, os.getcwd())

#import logging




    # importing from application packages
from implementation.parser_downloader import ParserDownloader

parse_downloader = ParserDownloader()
url = "https://www.elegantthemes.com/blog/wp-content/uploads/2015/02/custom-trackable-short-url-feature.png"
#url="https://s6t4u3w6.ssl.hwcdn.net/2017/8/514999/mp4/1.mp4"
#url = "https://34nk/##12.de/pk.html"
parse_downloader.download_image(url)