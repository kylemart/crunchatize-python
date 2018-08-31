import requests


API_URL = 'https://api.groupme.com/v3/'


class GroupMeBot:

    POST_URL = API_URL + 'bots/post'

    def __init__(self, bot_id):
        """
        :param bot_id: The id of the GroupMe bot
        """
        self.bot_id = bot_id

    def post(self, text):
        """
        :param text: The text to post via the GroupMe bot
        """
        try:
            data = {'bot_id': self.bot_id, 'text': text}
            response = requests.post(GroupMeBot.POST_URL, data)
            response.raise_for_status()

        except requests.exceptions.RequestException as ex:
            raise GroupMeRequestException(ex)


class GroupMeRequestException(ConnectionError):
    """
    Indicates a failed request with a GroupMe service or endpoint
    """
