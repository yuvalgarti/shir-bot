import json
import random

import requests


def send_dicta_request(data):
    body = {"task": "nakdan", "data": str(data), "genre": "modern"}
    headers = {'Content-type': 'text/plain;charset=UTF-8', 'accept-encoding': 'gzip, deflate, br'}
    response = requests.post('https://nakdan-3-0a.loadbalancer.dicta.org.il/api', json=body, headers=headers)
    return json.loads(response.text)


def dicta_words_as_list(dicta_result):
    result = []
    for word in dicta_result:
        if len(word['options']) > 0:
            result.append(word['options'][0].replace('|', ''))
        else:
            result.append(word['word'])
    return result


def get_dicta_nikud_as_list(text):
    return dicta_words_as_list(send_dicta_request(text))


def replace_random_spaces_with_newline(dicta_list):
    num_chars_between_spaces = 25
    num_chars_in_list = len(''.join(dicta_list))
    num_spaces = 0 if num_chars_in_list <= num_chars_between_spaces else int(
        num_chars_in_list / num_chars_between_spaces)
    space_indexes = [i for i, x in enumerate(dicta_list) if x == ' ']
    spaces_to_replace = random.choices(space_indexes, k=num_spaces)
    for i in spaces_to_replace:
        dicta_list[i] = '\n'
    return dicta_list


def get_dicta_nikud(text):
    return ''.join(replace_random_spaces_with_newline(get_dicta_nikud_as_list(text)))


def get_dicta_tweet_text(text, screen_name):
    return get_dicta_nikud(text) + '\n\n' + 'מקור: ' + '@' + screen_name
