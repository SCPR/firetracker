from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup
import mechanize
import urllib
import urllib2
import cookielib

class BaseScraper():
    @staticmethod
    def retrieve_source_html_with_mechanize(url_target):
        ''' new instance of mechanize browser '''
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
        raw_html = mech.open(url_target)
        raw_html = raw_html.read()
        return raw_html

    @staticmethod
    def save_source_html_to_file(file_name, raw_html):
        with open(file_name, 'wb', buffering=0) as new_file:
            new_file.write(raw_html)
        new_file.close()

    @staticmethod
    def convert_source_html_to_soup(raw_html):
        soup_html = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup_html