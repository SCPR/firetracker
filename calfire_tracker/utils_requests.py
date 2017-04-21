#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import management
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup
import logging
import datetime
import time

logger = logging.getLogger("calfire_tracker")


class Requester(object):
    """
    a series of reusable methods if you
    change something in here you're gonna
    want to change something in the
    test_utils_request script as well
    """

    date_object = datetime.datetime.now()
    date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")
    log_message = "\n*** Beginning Request ***\n"

    def _make_request_to(self, url):
        """
        make request to url and return response content
        """
        logger.debug("Requesting %s" % (url))
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        response = session.get(
            url,
            headers=settings.REQUEST_HEADERS,
            timeout=10,
            allow_redirects=False
        )
        try:
            response.raise_for_status()
            return response.content
        except requests.exceptions.ReadTimeout as exception:
            # maybe set up for a retry, or continue in a retry loop
            logger.error("%s: %s" % (exception, url))
            raise
        except requests.exceptions.ConnectionError as exception:
            # incorrect domain
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to raise message that we can't connect")
            raise
        except requests.exceptions.HTTPError as exception:
            # http error occurred
            logger.error("%s: %s" % (exception, url))
            logger.error("trying to access archived file via failsafe")
            raise
        except requests.exceptions.URLRequired as exception:
            # valid URL is required to make a request
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to raise message that URL is broken")
            raise
        except requests.exceptions.TooManyRedirects as exception:
            # tell the user their url was bad and try a different one
            logger.error("%s: %s" % (exception, url))
            logger.error("will need to raise message that URL is broken")
            raise
        except requests.exceptions.RequestException as exception:
            # ambiguous exception
            logger.error("%s: %s" % (exception, url))
            logger.error("trying to access archived file via failsafe")
            raise


    def _make_soup_from(self, raw_html):
        """
        creates beautiful soup from raw html
        """
        logger.debug("Converting content to HTML")
        soup = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup


    def _extract_simple_data_from(self, s):
        """
        creates beautiful soup from raw html
        """
        logger.debug("Finding targeted content")
        parent_content = s.soup.find(s.parent_tag, {s.parent_attrib: s.parent_selector})
        s.target_content = parent_content.findAll(s.target_tag, {s.target_attrib: s.target_selector})[s.target_index:]
        return s
