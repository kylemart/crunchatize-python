from diskcache import DiskCache
from groupme import GroupMeBot, GroupMeRequestException
from praw import Reddit
from queue import Queue
import crunchyroll
import re
import threading


comments = Queue()


def collect_reddit_comments(reddit):
    """
    Monitors '/r/crunchyroll' for guest pass codes
    :param reddit: A reddit bot instance
    """
    subreddit = reddit.subreddit('crunchyroll')
    for comment in subreddit.stream.comments():
        if comment.link_title.startswith('Weekly Guest Pass MegaThread'):
            comments.put(comment.body)


def collect_crunchyroll_comments():
    """
    Monitors the 'The Official Guest Pass Thread' for guest pass codes
    """
    for comment in crunchyroll.comment_stream('803801'):
        comments.put(comment.body)


def process_comments(bot, cache):
    """
    Processes each comment generated by the guess pass code collectors
    :param bot: A GroupMe bot instance
    :param cache: A disk-backed cache for storing / querying guest pass codes
    """
    while True:
        comment = comments.get()
        for code in re.findall('[A-Z0-9]{11}', comment):
            try:
                if code in cache:
                    continue
                link = crunchyroll.coupon_redeem_link(code)
                bot.post(code + ' 🎟 ' + link)
                cache.put(code)
            except GroupMeRequestException:
                print('Failed to send ' + code)


def main():

    cache = DiskCache('cache.json')
    bot = GroupMeBot('')
    reddit = Reddit(client_id='',
                    client_secret='',
                    user_agent='crunchatize:1.1 (by /u/kylemart)')

    threads = [
        threading.Thread(target=collect_crunchyroll_comments),
        threading.Thread(target=collect_reddit_comments, args=(reddit,)),
        threading.Thread(target=process_comments, args=(bot, cache))
    ]

    for thread in threads:
        thread.start()


if __name__ == '__main__':
    main()
