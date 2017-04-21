from django.test import SimpleTestCase, TestCase
from django.conf import settings
from calfire_tracker.models import WildfireSource
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup
import datetime
import logging
import re

logger = logging.getLogger("calfire_tracker")


class Compiler(TestCase):

    fixtures = ["calfire_tracker/fixtures/wildfire_sources.json"]

    def setUp(self):
        """
        setup some variables for our tests
        """
        logger.debug("Setting up tests")
        self.date_object = datetime.datetime.now()
        self.date_string = self.date_object.strftime("%Y_%m_%d_%H_%M_%S")
        self.source = WildfireSource.objects.filter(source_short="calfire", source_active=True)[0]


    def test_init(self, *args, **kwargs):
        """
        """
        self.source.raw_html = self.Test_make_request_to(self.source.source_url)
        self.source.soup = self.Test_make_soup_from(self.source.raw_html)
        if self.source.extraction_type == "Simple Scrape":
            self.Test_extract_simple_data_from(self.source)
        else:
            logger.debug("need a new scraper")
        logger.debug("Testing Completed")

    def Test_make_request_to(self, url):
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
            self.assertEquals(response.status_code, 200)
            self.assertIsNotNone(response.content)
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
            failsafe = self.Test_return_archived_file(src, data_directory)
            raise


    def Test_make_soup_from(self, raw_html):
        """
        creates beautiful soup from raw html
        """
        logger.debug("Converting content to HTML")
        soup = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.assertIsNotNone(soup)
        return soup


    def Test_extract_simple_data_from(self, src):
        """
        creates beautiful soup from raw html
        """
        logger.debug("Finding targeted content")
        parent_content = src.soup.find(src.parent_tag, {src.parent_attrib: src.parent_selector})
        self.assertIsNotNone(parent_content)
        src.target_content = parent_content.findAll(
            src.target_tag, {
            src.target_attrib: src.target_selector
        })[src.target_index:]
        self.assertIsNotNone(src.target_content)
        return src


class Normalizer(TestCase):

    def setUp(self):
        """
        setup some variables for our tests
        """
        logger.debug("Setting up tests")
        self.list_of_values = [
            "4347 acres - 5 % contained",
            "4347 acres - 5% contained",
            "4347 acres - 5 %contained",
            "4347 acres - 5%contained",
            "4347 acres - 5 percent contained",
            "4347 acres - 5percent contained",
            "4347 acres - 5 percentcontained",
            "4347 acres - 5percentcontained",
            "4347 acres - 33 % contained",
            "4347 acres - 33% contained",
            "4347 acres - 33 %contained",
            "4347 acres - 33%contained",
            "4347 acres - 33 percent contained",
            "4347 acres - 33percent contained",
            "4347 acres - 33 percentcontained",
            "4347 acres - 33percentcontained",
            "4,347 acres - 33 % contained",
            "4,347 acres - 33% contained",
            "4,347 acres - 33 %contained",
            "4,347 acres - 33%contained",
            "4,347 acres - 33 percent contained",
            "4,347 acres - 33percent contained",
            "4,347 acres - 33 percentcontained",
            "4,347 acres - 33percentcontained",
            "347 acres - 33 % contained",
            "347 acres - 33% contained",
            "347 acres - 33 %contained",
            "347 acres - 33%contained",
            "347 acres - 33 percent contained",
            "347 acres - 33percent contained",
            "347 acres - 33 percentcontained",
            "347 acres - 33percentcontained",
            "4347 acres - 100 % contained",
            "4347 acres - 100% contained",
            "4347 acres - 100 %contained",
            "4347 acres - 100%contained",
            "4347 acres - 100 percent contained",
            "4347 acres - 100percent contained",
            "4347 acres - 100 percentcontained",
            "4347 acres - 100percentcontained",
            "4,347 acres - 100 % contained",
            "4,347 acres - 100% contained",
            "4,347 acres - 100 %contained",
            "4,347 acres - 100%contained",
            "4,347 acres - 100 percent contained",
            "4,347 acres - 100percent contained",
            "4,347 acres - 100 percentcontained",
            "4,347 acres - 100percentcontained",
            "347 acres - 100 % contained",
            "347 acres - 100% contained",
            "347 acres - 100 %contained",
            "347 acres - 100%contained",
            "347 acres - 100 percent contained",
            "347 acres - 100percent contained",
            "347 acres - 100 percentcontained",
            "347 acres - 100percentcontained",
            "347 - 100 % contained",
            "347 - 100% contained",
            "347 - 100 %contained",
            "347 - 100%contained",
            "347 - 100 percent contained",
            "347 - 100percent contained",
            "347 - 100 percentcontained",
            "347 - 100percentcontained",
            "347 - 100percentcontained",
            "percent contained",
            "% contained",
            "contained",
            "191 acres",
            "19 contained",
            "19contained",
            "100% contained ***This is not a CAL FIRE incident, For more information click on the link above",
        ]


    def test_init(self, *args, **kwargs):
        """
        """
        for item in self.list_of_values:
            self.Test_extract_acres(item)
            self.Test_extract_containment(item)
        logger.debug("Testing Completed")


    def Test_extract_acres(self, string):
        """
        runs regex on acres cell to return acres burned as int
        """
        extract_surrounded_number = re.compile("(\d+)")
        string = string.replace(",", "").replace(" - ", " ").strip()
        acres_match = re.search("acres", string)
        if acres_match:
            acres = re.findall(extract_surrounded_number, string)
        else:
            sign_match = re.search("%", string)
            percent_match = re.search("percent", string)
            contain_match = re.search("contain", string)
            if sign_match:
                acres = re.findall(extract_surrounded_number, string)
            elif percent_match:
                acres = re.findall(extract_surrounded_number, string)
            elif contain_match:
                acres = re.findall(extract_surrounded_number, string)
            else:
                acres = re.findall(extract_surrounded_number, string)
            logger.debug(acres)


        # try:
        #     if len(acres) == 2:
        #         target_number = acres[0]
        #     elif len(acres) == 1:
        #     elif len(acres) == 0:
        #         target_number = None
        #     else:
        #         target_number = None
        # except Exception, exception:
        #     logger.error("%s" % (exception))
        #     raise

        # logger.debug(target_number)


        # sign_match = re.search("acres", string)

        # number_check = re.compile("\d+\sacres")
        # extract_acreage = re.compile("\d+\sacres")
        # extract_number = re.compile("^\d+")
        # match = re.search(number_check, target_number)
        # if match:
        #     try:
        #         target_number = re.search(extract_acreage, target_number).group()
        #         target_number = re.search(extract_number, target_number).group()
        #         target_number = int(target_number)
        #         self.assertIsInstance(target_number, int)
        #     except Exception, exception:
        #         logger.error("%s" % (exception))
        #         raise
        # else:
        #     match = re.search(extract_number, target_number)
        #     if match:
        #         try:
        #             target_number = re.search(extract_number, target_number).group()
        #             target_number = int(target_number)
        #             self.assertIsInstance(target_number, int)
        #         except Exception, exception:
        #             logger.error("%s" % (exception))
        #             raise
        #     else:
        #         target_number = None
        #         self.assertIsNone(target_number)



    def Test_extract_containment(self, string):
        """
        runs regex on acres cell to return containment as int
        """
        extract_surrounded_number = re.compile("(\d+)")
        string = string.replace(",", "").replace(" - ", " ").strip()
        sign_match = re.search("%", string)
        percent_match = re.search("percent", string)
        contain_match = re.search("contain", string)
        if sign_match:
            containment = re.findall(extract_surrounded_number, string)
        elif percent_match:
            containment = re.findall(extract_surrounded_number, string)
        elif contain_match:
            containment = re.findall(extract_surrounded_number, string)
        else:
            containment = []
        try:
            if len(containment) == 2:
                target_number = containment[1]
            elif len(containment) == 1:
                target_number = containment[0]
            elif len(containment) == 0:
                target_number = None
            else:
                target_number = None
        except Exception, exception:
            logger.error("%s" % (exception))
            raise
        if target_number:
            target_number = int(target_number)
            self.assertIsInstance(target_number, int)
        else:
            target_number = None
            self.assertIsNone(target_number)


    def slugify(self, string):
        """
        take a string and make it a slug
        """
        value = re.sub("[^0-9a-zA-Z\s-]+", " ", string.lower())
        pretty_name = " ".join(value.split())
        slug = pretty_name.encode("ascii", "ignore").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = re.sub(r"[-]+", "-", slug)
        return slug
