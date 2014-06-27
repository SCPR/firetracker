from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.db.models import Q, Avg, Max, Min, Sum, Count
from calfire_tracker.models import CalWildfire, WildfireDisplayContent
from dateutil import parser
from datetime import datetime, date, time, timedelta
import pytz, logging, re
from pytz import timezone

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

register = Library()

def rows(thelist, n):
    """
    Break a list into ``n`` rows, filling up each row to the maximum equal
    length possible. For example::

        >>> l = range(10)

        >>> rows(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> rows(l, 3)
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

        >>> rows(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        >>> rows(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> rows(l, 9)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [], [], [], []]

        # This filter will always return `n` rows, even if some are empty:
        >>> rows(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n

    if list_len % n != 0:
        split += 1
    return [thelist[split*i:split*(i+1)] for i in range(n)]

def rows_distributed(thelist, n):
    """
    Break a list into ``n`` rows, distributing columns as evenly as possible
    across the rows. For example::

        >>> l = range(10)

        >>> rows_distributed(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> rows_distributed(l, 3)
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> rows_distributed(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 9)
        [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]]

        # This filter will always return `n` rows, even if some are empty:
        >>> rows(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n

    remainder = list_len % n
    offset = 0
    rows = []
    for i in range(n):
        if remainder:
            start, end = (split+1)*i, (split+1)*(i+1)
        else:
            start, end = split*i+offset, split*(i+1)+offset
        rows.append(thelist[start:end])
        if remainder:
            remainder -= 1
            offset += 1
    return rows

def columns(thelist, n):
    """
    Break a list into ``n`` columns, filling up each column to the maximum equal
    length possible. For example::

        >>> from pprint import pprint
        >>> for i in range(7, 11):
        ...     print '%sx%s:' % (i, 3)
        ...     pprint(columns(range(i), 3), width=20)
        7x3:
        [[0, 3, 6],
         [1, 4],
         [2, 5]]
        8x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5]]
        9x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
        10x3:
        [[0, 4, 8],
         [1, 5, 9],
         [2, 6],
         [3, 7]]

        # Note that this filter does not guarantee that `n` columns will be
        # present:
        >>> pprint(columns(range(4), 3), width=10)
        [[0, 2],
         [1, 3]]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    return [thelist[i::split] for i in range(split)]

def percentify(value):
    if value == 0:
        return str(value) + '%'
    elif value == None:
        return 'n/a'
    else:
        return str(value) + '%'

def create_date(value):
    display_date = parser.parse(value)
    return display_date

def format_for_timezone(value):
    ''' working some crazy datetime magic that might be working '''
    ''' based on http://stackoverflow.com/questions/17193228/python-twitter-api-tweet-timestamp-convert-from-utc-to-est '''
    utc = timezone('UTC')
    utc_created_at = utc.localize(value)
    return utc_created_at

def resource_content_to_include(value):
    ''' returns the resource list queryset to the default flatpage template '''
    resource_content = WildfireDisplayContent.objects.filter(Q(resource_content_type=True) & Q(display_content_type=True) | Q(resource_content_type=True)).order_by('content_headline')
    return resource_content

def all_fires_to_include(value):
    ''' returns the 15 recent fire list queryset to the default flatpage template '''
    result_list = CalWildfire.objects.exclude(containment_percent=None).order_by('-date_time_started', 'fire_name', 'containment_percent')[0:15]
    return result_list

def eval_closeout(value):
    if value == True:
        return "close-me"
    else:
        return "display-me"

register.filter(rows)
register.filter(rows_distributed)
register.filter(columns)
register.filter(percentify)
register.filter(create_date)
register.filter(format_for_timezone)
register.filter(resource_content_to_include)
register.filter(all_fires_to_include)
register.filter(eval_closeout)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()