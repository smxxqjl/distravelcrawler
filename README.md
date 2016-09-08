# A distributed travel info crawler
This is a distributed travel infomation crawler base on scrapy and redis.
To use, run redis and python script redis_control.py in master. And edit master ip address in distravelcrawler/settings.py.
The run by typing `scrapy crawl mainspider` in every slave. Each slave would get url from redis server and process it,
and store the result into remot mongodb server.
