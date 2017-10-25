# trulia-scraper
Scraper for real estate listings on [Trulia.com](https://www.trulia.com/) implemented in Python with Scrapy.

## Basic usage
To crawl the scraper, you need to install [Python 3](https://www.python.org/download/releases/3.0/), as well as the [Scrapy](https://pypi.python.org/pypi/Scrapy) framework and the [Pyparsing](https://pypi.python.org/pypi/pyparsing/2.2.0) module. The scraper features two spiders:

1. `trulia`, which scrapes all real estate listings which are _for sale_ in a given state and city starting from a URL such as [https://www.trulia.com/CA/San_Francisco/](https://www.trulia.com/CA/San_Francisco/);
2. `trulia_sold`, which similarly scrapes listings of recently _sold_ properties starting from a URL such as [https://www.trulia.com/sold/San_Francisco,CA/](https://www.trulia.com/sold/San_Francisco,CA/).

To crawl the `trulia_sold` spider for the state of `CA` and city of `San_Francisco` (the default locale), simply run the command

```
scrapy crawl trulia_sold
```
from the project directory. To scrape listings for another city, specify the `city` and `state` arguments using the `-a` flag. For example,

```
scrapy crawl trulia_sold -a state=NY -a city=New_York
```
will scrape all listings reachable from [https://www.trulia.com/sold/New_York,NY/](https://www.trulia.com/sold/New_York,NY/).

By default, the scraped data will be stored (using Scrapy's [feed export](https://doc.scrapy.org/en/latest/topics/feed-exports.html)) in the `data` directory as a [JSON lines](http://jsonlines.org/) (`.jl`) file following the naming convention

```
data_{sold|for_sale}_{state}_{city}_{time}.jl
```

where `{sold|for_sale}` is `sold` or `for_sale` for the `trulia` and `trulia_sold` spiders, respectively, `{state}` and `{city}` are the specified state and city (e.g. `CA` and `San_Francisco`, respectively), and `{time}` represents the current UTC time.

If you prefer a different output file name and format, you can specify this from the command line using Scrapy's `-o` option. For example,

```
scrapy crawl trulia_sold -a state=WA -city=Seattle -o data_Seattle.csv
```
will output the data in CSV format as `data_Seattle.csv`. (Scrapy automatically picks up the file format from the specified file extension).