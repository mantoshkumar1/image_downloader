#!/bin/sh

# Reference: https://lincolnloop.com/blog/filtering-results-coveragepy/

# Erasing previously collected coverage data
coverage erase

# Run a Python program and collect execution data.
coverage run -m unittest discover

# Produce annotated HTML listings with coverage results.
coverage html

# Opening code coverage report in default browser
echo 'Opening code coverage report in default browser'
# https://stackoverflow.com/questions/3124556/clean-way-to-launch-the-web-browser-from-shell-script?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
python -m webbrowser ./documentation/coverage_html_report/index.html
