from implementation.parser_downloader import ParserDownloader
from settings import configure_application

# configuring application using defined configurations
configure_application()

parse_downloader = ParserDownloader()

url = "https://www.elegantthemes.com/blog/wp-content/uploads/2015/02/custom-trackable-short-url-feature.png"
#url="https://s6t4u3w6.ssl.hwcdn.net/2017/8/514999/mp4/1.mp4"
#url = "https://34nk/##12.de/pk.html"
parse_downloader.download_image(url)
