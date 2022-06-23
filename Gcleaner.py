from googleapiclient.errors import HttpError
import time
import random
from alive_progress import alive_it
from GClient import GClient


dict_count = {}


def batchcallbackfunc(request_id, response, exception):
    # A callback to be called for each response
    if exception is not None:
        print(exception)
        print("riprovo dopo una pausa di 60 sec")
        time.sleep(60+random.randint(0, 5))
    else:
        try:
            if response["payload"]["headers"][0]["value"] in dict_count:
                dict_count[response["payload"]["headers"][0]["value"]] += 1
            else:
                dict_count.update({response["payload"]["headers"][0]["value"]: 1})
        except:
            print("Error")


def list_id_messages(self, user_id="me"):
    '''
    Lists all the messages in the user's mailbox.

    Args:
        userId: string, The user's email address. The special value
        `me` can be used to indicate the authenticated user. (required)

    Returns:
        A list with gmail message id
    '''

    try:
        messages = []
        response = self.users().messages().list(userId="me", q="from:-me", maxResults=500).execute()
        if "nextPageToken" in response:
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.users().messages().list(userId="me", q="from: -me", pageToken=page_token, maxResults=500).execute()
                for message in response['messages']:
                    messages.append(message['id'])
        else:
            for message in response['messages']:
                messages.append(message['id'])
        return messages

    except Exception as error:
        print(f'An error occurred at list_messages: {error}')


def dict_senders():
    '''
    Returns:
        A dict with Received emails key and numbers value
    '''
    try:
        service = GClient().service
        id_messages = list_id_messages(service)
        print("Ci sono {} MAIL".format(len(id_messages)))
        for i in alive_it(range(0, len(id_messages), 50)):
            batch = service.new_batch_http_request(callback=batchcallbackfunc)
            for id in id_messages[i:i+50]:
                batch.add(service.users().messages().get(userId='me', id=id, format="metadata", metadataHeaders=["From"]))
            batch.execute()
            time.sleep(1)  # API rate limit , 250 quota units per user per second, GET = 5 unit

        sorted_tuples = sorted(dict_count.items(), key=lambda item: item[1], reverse=True)
        sorted_tuples = {k: v for k, v in sorted_tuples}
        return sorted_tuples
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def main():
    senders = dict_senders()
    iterator = iter(senders.items())
    for i in range(10):
        print(next(iterator))


if __name__ == '__main__':
    main()
