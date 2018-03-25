from implementation.app_constants import *

APP_CFG = {
    # Path of the document which contains urls of images (for simplicity use absolute path)
    IMAGE_URLS_FILE_PATH : './image_urls.txt',


    # Location where downloaded files will get stored (for simplicity use absolute path)
    IMAGE_SAVE_DIR : './downloaded_images',


    # URL_TIMEOUT parameter specifies Requests to stop waiting for a response after a \
    # specified number of seconds. It avoids the application to hang indefinitely.\
    # In case of timeout, it reattempts to download the URL path "MAX_DOWNLOAD_ATTEMPTS_PER_URL" times.
    # If you need to configure the application to wait for a response indefinitely, please assign None to it.
    # You are strongly advised to provide a timeout value.
    URL_TIMEOUT: 2,


    # In case of URL_TIMEOUT, MAX_DOWNLOAD_REATTEMPTS specifies number of maximum attempts to \
    # download an URL resource. Set it to None, if you prefer not to reattempt. \
    # If "URL_TIMEOUT" is already set to None, application ignores this configuration.
    MAX_DOWNLOAD_REATTEMPTS : 2,


    # If you need to use a proxy, assign a dictionary (e.g; using proxies argument) mapping protocol \
    # or protocol and host to the URL of the proxy to be used on each Request using SYSTEM_PROXY configuration. \
    # Otherwise configure it to a None.
    # For detailed info, please visit http://docs.python-requests.org/en/master/user/advanced/#proxies
    # proxies : {
    #     'http': 'http://10.10.1.10:3128',
    #     'https': 'http://10.10.1.10:1080',
    # }
    SYSTEM_PROXY: None,
}