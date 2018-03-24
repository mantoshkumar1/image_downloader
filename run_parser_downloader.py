from implementation.parser_downloader import ParserDownloader

parse_downloader = ParserDownloader()
url = "https://www.elegantthemes.com/blog/wp-content/uploads/2015/02/custom-trackable-short-url-feature.png"
parse_downloader.download_image(url)