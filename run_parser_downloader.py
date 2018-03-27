from settings import configure_application
from implementation.downloader import Downloader
from implementation.parser import FileParser

# configuring application using defined configurations
configure_application()

# starting file parser
fp = FileParser()
fp.start_parser_thread()

# starting url downloader threads
url_dl = Downloader(fp.url_queue)
url_dl.start_downloader_threads()

# waiting for parser thread
fp.wait_for_parser_thread()

# waiting for downloader threads
url_dl.wait_for_downloader_threads()
