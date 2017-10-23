# trulia-scraper
Scraper for real estate listings on Trulia.com implemented in Python with Scrapy.

## Basic usage
To crawl the scraper, you need to install [Python 3](https://www.python.org/download/releases/3.0/), as well as the [Scrapy](https://pypi.python.org/pypi/Scrapy) framework and the [Pyparsing](https://pypi.python.org/pypi/pyparsing/2.2.0) module. The scraper features two spiders:

1. `trulia`, which is designed to scrape all real estate listings which are for sale in a given state and city starting for a URL such as [https://www.trulia.com/CA/San_Francisco/](https://www.trulia.com/CA/San_Francisco/);
2. `trulia_sold`, which similarly scrapes listings of recently sold properties starting from URLs like [https://www.trulia.com/sold/San_Francisco,CA/](https://www.trulia.com/sold/San_Francisco,CA/).

To, for example, crawl `trulia_sold` in the state of `CA` in the city of `San_Francisco` (the default locale for both spiders), simply run the command

```
scrapy crawl trulia_sold
```
from the project directory. This will generate a [feed export](https://doc.scrapy.org/en/latest/topics/feed-exports.html) as a [JSON lines](http://jsonlines.org/) (`.jl`) file in one of the following default locations:

* `data/data_sold.jl` for data scraped by the `trulia_sold` spider,
* `data/data_for_sale.jl` for data scraped by the `trulia` spider.

(The repository includes instances of both files scraped on 22 October 2016). You can choose a different file location and output format using the `--output` and `--output-format` command-line options (see `scrapy crawl --help` for details); supported formats include regular JSON and CSV.

To scrape listings from a city other than San Francisco, specify the `city` and `state` arguments using the `-a` flag. For example,

```
scrapy crawl trulia_sold -a state=NY city=New_York -o data/data_New_York.jl
```
will scrape all listings reachable from [https://www.trulia.com/sold/New_York,NY/](https://www.trulia.com/sold/New_York,NY/) and save the data to an accordingly named output file `data_New_York.jl` in the `data` directory.