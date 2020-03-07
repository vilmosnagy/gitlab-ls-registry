import os
import requests

GITLAB_URL = os.environ['GITLAB_URL']
GITLAB_USERNAME = os.environ['GITLAB_USERNAME']
GITLAB_TOKEN = os.environ['GITLAB_TOKEN']


def get_paged_api(url):
    page = 1
    ret_array = []
    response = get_api(url, page)
    response_array = []
    if response.status_code < 300:
        response_array = response.json()
    ret_array += response_array
    while len(response_array) > 0:
        page += 1
        response = get_api(url, page)
        if response.status_code < 300:
            response_array = response.json()
            ret_array += response_array
    return ret_array


def get_api(url, page=None):
    url = f"{GITLAB_URL}/{url}"
    if not url.__contains__('?'):
        url = f"{url}?private_token={GITLAB_TOKEN}"
    else:
        url = f"{url}&private_token={GITLAB_TOKEN}"
    if page:
        url = url + f"&page={page}"
    return requests.get(url)


def delete_api(url, page=None):
    url = f"{GITLAB_URL}/{url}"
    if not url.__contains__('?'):
        url = f"{url}?private_token={GITLAB_TOKEN}"
    else:
        url = f"{url}&private_token={GITLAB_TOKEN}"
    if page:
        url = url + f"&page={page}"
    return requests.delete(url)
