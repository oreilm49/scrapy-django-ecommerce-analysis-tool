class ScraperException(Exception):
    """Raised for general errors"""


class WebsiteNotProvidedInArguments(ScraperException):
    """Raised with website not provided to spider"""
