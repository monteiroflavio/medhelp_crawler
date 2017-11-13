from urllib.request import urlopen as uo
import urllib.error

def fetch_url(url):
    try:
        web_client = uo(url)
        if web_client.getcode() == 504:
            raise ConnectionError('gateway timeout')
        web_page = web_client.read()
    except urllib.error.HTTPError as e:
        raise ConnectionError('http error occurred')
    except urllib.error.URLError as e:
        raise ConnectionError('http error occurred')
    else:
        web_client.close()
        return web_page

def handle_req_tries(url, max_tries):
    for i in range(max_tries):
        try:
            web_page = fetch_url(url)
        except ConnectionError:
            raise ConnectionError('required url didn\'t respond')
        else:
            return web_page
