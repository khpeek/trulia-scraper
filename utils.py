# -*- coding: utf-8 -*-
# @Time    : 19-10-22 下午3:46
# @Author  : RenMeng

from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse
from posixpath import normpath


def get_rel_url(cur_url, rel_url):
    if not rel_url.startswith("./") and not rel_url.startswith("/"):
        return rel_url
    url1 = urljoin(cur_url, rel_url)
    arr = urlparse(url1)
    path = normpath(arr[2])
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

