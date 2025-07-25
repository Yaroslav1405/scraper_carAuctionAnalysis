# Scraper carAuctionAnalysis

This is part of the [carAuctionAnalysis](https://github.com/Yaroslav1405/carAuctionAnalysis) project. The data was scraped from _bid.cars_ and was freely accessible to everyone at the time of scraping.

When starting a project, the website's structure differed from the final version. I believe that while developing code for scraping, I encountered website maintenance and restructuring. Because of this, the scraper had to be reworked to align with the new website structure. 

## Tools used
* Selenium - to open the web page and load all elements.
* Beautiful Soup - to load the page source in the lxml format, and extract necessary data.
* Pandas - to create a dataframe file and concatenate results.
* Time - sleep between scraping processes to reduce load on the server.
