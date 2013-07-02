import mechanize
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

class BaseScraper():

    @staticmethod

    # new instance of mechanize browser
    def create_instance_of_mechanize(url_target):
        # new instance of mechanize browser
        mech = mechanize.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        mech.set_cookiejar(cj)

        # mechanize browser options
        mech.set_handle_equiv(True)
        mech.set_handle_redirect(True)
        mech.set_handle_referer(True)

        # tell mechanize browser to ignore robots.txt
        mech.set_handle_robots(False)

        # follows refresh 0 but not hangs on refresh > 0
        mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # adds user-Agent
        mech.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19')]

        page_scrape = mech.open(url_target)
        html_scrape = page_scrape.read()
        soup_scrape = BeautifulSoup(html_scrape, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup_scrape