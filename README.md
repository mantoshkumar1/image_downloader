# File Parser - Web Image Downloader
This application takes a plaintext file as an argument which contains image URLs, one per line. The application parses the
plaintext file and downloads all serviceable image urls, and finally stores them on user-defined location on the local hard disk.
 

# How to install the application software requirements:
<code>$ cd image_downloader</code>
- If you want to install and use the required packages:<br>
<code>$ python setup.py install</code>
- Instead, if you don't want to install the required packages, however, still would like to use them, then execute:<br>
<code>$ python setup.py develop</code>

This application has been developed and tested on Ubuntu 16.04 LTS OS using Python 3.5.2. For other OS platform, few instructions might need to be adapted.

# How to run the application
<code>$ cd image_downloader</code><br>
<code>$ python run_parser_downloader.py <file_path></code>

Example:  <code>$ python run_parser_downloader.py ./image_urls.txt</code>

#How to run the unittests
First run the application in a terminal and execute the following command in another terminal 

$ cd image_downloader 
todo: write more about it. 

Future Extension / Optimization
----------------------------------------
- In future, if the list of URLs contains only certain sites, then from network connection point of view, 
it would be optimizable to only hit a single site with one request at a time (use a delay or send
all URLs per site to a single thread/process). Using a single thread/process per site can help save
the overhead of a three-way TCP handshake for HTTP persistent connections, however, this proposition is 
advisable only if you are performing multiple requests to the same host. Also, learn more about HTTP/1.1 request
pipelining and how to keep it alive.
- ***A word of caution:*** A very large thread pool size might quickly lead to diminishing application
performance based upon the configuration of your local system. I have employed one thread to parse the
file and four threads to perform multiple downloads at once. To make this application capable of
handling a massive list of url downloads, it is advised to increase the number of download threads
(up to certain limit, 
 otherwise context switching among threads might lead to disparaging application performance).
 However, use more number of threads than the number of CPUs in your local system. That way, 
 the application can wait for many slow hosts at the same time.
 - If you want to make this application capable of parallel execution on SMP and clusters, you can 
 consider incorporating [parallel python](https://www.parallelpython.com/) into this application.
 - It is possible to extend the capability of this application to crawl the web for the user-defined type
of resources due to its modular architecture. If you implement this feature, please do make sure to
honour the sites [robots.txt](http://www.robotstxt.org/robotstxt.html), otherwise the application
might likely get blocked pretty quickly by a single IP on a single site. [robotexclusionrulesparser](https://pypi.python.org/pypi/robotexclusionrulesparser) is 
a viable option to analyze robot.txt. A straightforward approach to avoid such blocking could be to
put a random sleep times in your crawler so that it does not multiple
request in a very short timespan. You can also employ a priority queue to store/fetch the sites
(used by threads) and based upon an intelligent algorithm, the application might issue request to
site. All of these approaches are only to outmanoeuvre the tarpit defense  mechanism of a site.  