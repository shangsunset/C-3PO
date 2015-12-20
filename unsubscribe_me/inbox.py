import base64
import pprint
import urllib3
from bs4 import BeautifulSoup


class Inbox():

    def __init__(self, gmail, access_token, user_id):
        self.gmail = gmail
        self.access_token = access_token
        self.email_senders = []
        self.user_id = user_id
        self.emails = self.get_emails()

    def get_emails(self):
        url = 'https://www.googleapis.com/gmail/v1/users/{}/messages?q=category:(promotions+OR+primary)+newer_than:14d'.format(self.user_id)
        messages = []

        try:
            res = self.gmail.get(url)
            if 'messages' in res.data:
                messages.extend(res.data['messages'])
            while 'nextPageToken' in res.data:
                page_token = res.data['nextPageToken']
                new_url = '{url}&pageToken={page_token}'.format(url=url, page_token=page_token)
                res = self.gmail.get(new_url)
                messages.extend(res.data['messages'])
        except urllib3.exceptions.HTTPError as err:
            print(err.code)

        emails = []
        for message in messages:
            email = self.get_unsubscribe_info(message['id'])

            if email is not None:
                emails.append(email.copy())

        return emails
        # return messages

    def get_unsubscribe_info(self, email_id):
        """
        get email sender name, address, and unscribe link from email header
        returns a dict contains sender'name and unsubscribe methods
        """
        url = 'https://www.googleapis.com/gmail/v1/users/{}/messages/{}'.format(self.user_id, email_id)
        response = self.gmail.get(url)
        payload = response.data['payload']

        unsubscribe_info = {'email_id': email_id}
        unsubscribe_methods = {}
        is_newsletter = False
        headers = payload['headers']
        for header in headers:
            if header['name'].lower() == 'from':
                value = header['value']
                # value = 'sender name <example@email.com>'
                # name = value[:value.index('<')]
                text = value.split()[:-1]
                name = ' '.join([i for i in text])
                name = ''.join([i if ord(i) < 128 else '' for i in name])
                unsubscribe_info['sender_name'] = name.strip('\" ')

                if unsubscribe_info['sender_name'] not in self.email_senders:
                    self.email_senders.append(unsubscribe_info['sender_name'])
                else:
                    return None

            if header['name'].lower() == 'list-unsubscribe':
                is_newsletter = True
                value = header['value'].strip()
                if ',' in value:  # if there are more than one unsubscribe method
                    methods = value.split(',')
                    for method in methods:
                        if 'mailto' in method:
                            unsubscribe_methods['mailto'] = method.strip('<>')
                        else:
                            unsubscribe_methods['link'] = method.strip('<>')
                else:
                    method = value.strip('<>')
                    if 'mailto' in method:
                        unsubscribe_methods['mailto'] = method
                    else:
                        unsubscribe_methods['link'] = method

                unsubscribe_info['unsubscribe_methods'] = unsubscribe_methods

        if is_newsletter:
            return unsubscribe_info

        return None

    # def scan_through_emails(self, email_id):
    #     """
    #     get email sender, content from gmail api response object
    #     return dict
    #     """
    #
    #     url = 'https://www.googleapis.com/gmail/v1/users/{}/messages/{}'.format(self.user_id, email_id)
    #     response = self.gmail.get(url)
    #     payload = response.data['payload']
    #
        # if 'parts' in payload:
        #     if len(payload['parts']) > 1:
        #         body = payload['parts'][1]['body']['data']
        #     else:
        #         if 'parts' in payload['parts'][0]:
        #             body = payload['parts'][0]['parts'][0]['body']['data']
        #         else:
        #             body = payload['parts'][0]['body']['data']
        # else:
        #     body = payload['body']['data']
        #
        # decoded_body = base64.b64decode(body.replace('-', '+').replace('_', '/'))
        # return {'email_id': email_id, 'body': decoded_body}
