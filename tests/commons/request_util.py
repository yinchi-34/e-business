import requests


class RequestUtil:

    session =requests.session()

    def all_send_request(self, **kwargs):
        res = RequestUtil.session.request(**kwargs)
        print(res.text)
        return res