#!/bin/sh

# This shell script is used to generate code coverage of this application.
# coverage commands are using .coveragerc to control coverage.py

# Reference: https://lincolnloop.com/blog/filtering-results-coveragepy/

echo 'Erasing previously collected coverage data'
coverage erase

echo 'Running Python testsuits and collecting execution data'
coverage run -m unittest discover

echo 'Producing annotated HTML listings with coverage results'
coverage html

# https://stackoverflow.com/questions/3124556/clean-way-to-launch-the-web-browser-from-shell-script?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
echo 'Code coverage report has been opened in system default browser'
python -m webbrowser ./documentation/coverage_html_report/index.html

echo 'GoodBye!'
