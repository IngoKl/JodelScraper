# JodelScraper

This is a simple tool written in Python 3 that scrapes [Jodels](https://jodel.com/) (from *Jodel*) and associated replies and saves them in a SQLite database for further analysis. 

Under the hood, JodelScraper relies on `jodel_api` by nborrmann ([GitHub](https://github.com/nborrmann/jodel_api)).

The primary use case of JodelScraper is the fast compilation of Jodel corpora for (linguistic) analysis. Be  aware: using this tool could be considered a violation of the [Terms and Conditions](https://jodel.com/de/terms/).



## Usage

JodelScraper supports three modes:

`python jodel_scraper.py popular`

`python jodel_scraper.py discussed`

`python jodel_scraper.py recent`



## Issues

* The 'skip' argument `of get_post_details_v3` seems to not be reliable. Hence, threads beyond 50 comments are possibly not captured in their entirety.