from bs4 import BeautifulSoup
from collections import deque
import requests
import time


SITE_URL = 'http://www.crunchyroll.com'


class BoundedSet:

    def __init__(self, max_length):
        """
        :param max_length: The maximum allowable length for the set
        """
        self._q = deque(maxlen=max_length)
        self._s = set()

    def __contains__(self, item):
        """
        :param item: The item being checked for membership
        :return: True if the item is in the set; False otherwise
        """
        return item in self._s

    def __iter__(self):
        """
        :return: An iterable generator that can be used to traverse the set
        """
        for item in self._q:
            yield item

    def add(self, item):
        """
        Adds an item to the set. This method will remove the oldest element
        if including this new item would exceed the maximum length requirement.

        :param item: The item to add to the set
        """
        if item in self._s:
            return
        if self._q.maxlen and len(self._q) == self._q.maxlen:
            removing = self._q.popleft()
            self._s.remove(removing)
        self._q.append(item)
        self._s.add(item)


class Page:

    def __init__(self, html):
        """
        :param html: The html content of the page
        """
        self._root = BeautifulSoup(html, 'html.parser')

    @property
    def paginator_hrefs(self):
        """
        :return: A dictionary of paginator hrefs (key: title, val: href)
        """
        result = {}
        paginator = self._root.find('div', 'showforumtopic-paginator')
        for anchor in paginator.findAll('a'):
            attrs = anchor.attrs
            result[attrs['title']] = attrs['href']
        return result

    def comments(self):
        """
        :return: Each comment on the page
        """
        found = self._root.findAll('td', 'showforumtopic-message-contents')
        for comment in found:
            yield Comment(comment)


class Comment:

    def __init__(self, root):
        """
        :param root: The root html element encompassing the comment
        """
        self._root = root

    @property
    def permalink(self):
        """
        :return: The comment permalink
        """
        found = self._root.find('a', {'title': 'Permalink'})
        return found.attrs['href']

    @property
    def body(self):
        """
        :return: The stripped text of the comment body
        """
        found = self._root.find('div', 'showforumtopic-message-contents-text')
        return found.text.strip()


def comment_stream(topic_id):
    """
    :param topic_id: The id of a crunchyroll forum topic
    :return: An infinite stream of comments belonging to the forum topic
    """
    page_link = SITE_URL + '/forumtopic-' + topic_id + '?pg=last'
    ignore = BoundedSet(10)

    while True:
        try:
            response = requests.get(page_link)
            response.raise_for_status()

            page = Page(response.content)

            for comment in page.comments():
                permalink = comment.permalink
                if permalink in ignore:
                    continue
                ignore.add(permalink)
                yield comment

            next_href = page.paginator_hrefs.get('Next', None)
            if next_href:
                page_link = SITE_URL + next_href
                continue

            page_link = response.url
            time.sleep(1)

        except requests.exceptions.RequestException:
            time.sleep(5)


def coupon_redeem_link(code):
    """
    :param code: The code to generate the link for
    :return: A link that can be visited in order to redeem the code
    """
    return SITE_URL + '/coupon_redeem?code=' + code
