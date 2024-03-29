import sys
import os
import django
from django.conf import settings

BOT_NAME = 'scraper'

SPIDER_MODULES = ['cms.scraper.spiders']
NEWSPIDER_MODULE = 'cms.scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'scraper (+http://www.specr.ie)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scraper.middlewares.ScraperSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'scraper.middlewares.ScraperDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'scrapy.pipelines.images.ImagesPipeline': 100,
   'scraper.pipelines.ProductPipeline': 200,
   'scraper.pipelines.ProductAttributePipeline': 300,
   'scraper.pipelines.WebsiteProductAttributePipeline': 400,
   'scraper.pipelines.ProductImagePipeline': 500,
   'scraper.pipelines.PDFEnergyLabelConverterPipeline': 600,
   'scraper.pipelines.SpecFinderPDFEnergyLabelPipeline': 700,
}

IMAGES_FOLDER = 'product_images'
IMAGES_ENERGY_LABELS_FOLDER = f'{IMAGES_FOLDER}/energy_labels'
IMAGES_STORE = os.path.join(settings.MEDIA_ROOT, f'{IMAGES_FOLDER}')
IMAGES_ENERGY_LABELS_STORE = os.path.join(settings.MEDIA_ROOT, f'{IMAGES_ENERGY_LABELS_FOLDER}')
IMAGES_THUMBS = {
    'big': (270, 270),
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = os.environ.get('DEBUG') == 'true'

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = os.environ.get('HTTPCACHE_ENABLED') == 'true'
HTTPCACHE_EXPIRATION_SECS = os.environ.get('HTTPCACHE_EXPIRATION_SECS')
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Django integration
sys.path.append('/app')
django.setup()
