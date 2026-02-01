#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-01-19
Description:

core.lib.third.selenium is lots of wrappers around selenium that i've found or developed over the years.
core.lib are modules that contain code that is about (but does not modify) the library. somewhat referential to core.functor and core.types.

Updates:
    2026-01-31 - core.lib.third.selenium - added wait_for_element_or_driver and load_cookies
    2026-01-19 - core.lib.third.selenium - initial commit
'''

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
import json
import time
import datetime
import threading
from typing import Tuple, Optional, Union, Dict, List

# third party imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from websocket import WebSocketApp

# project imports
from chriscarl.core.lib.stdlib.os import abspath, make_dirpath
from chriscarl.core.lib.stdlib.urllib import get

SCRIPT_RELPATH = 'chriscarl/core/lib/third/selenium.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

DEFAULT_DOWNLOAD_DIRPATH = abspath('~/downloads')
DEFAULT_CHROME_DEBUG_PORT = 7654


def get_driver(
    url='https://google.com',
    download_directory=DEFAULT_DOWNLOAD_DIRPATH,
    port=DEFAULT_CHROME_DEBUG_PORT,
):
    # type: (str, str, int) -> WebDriver
    LOGGER.debug('launching browser')
    download_directory = abspath(download_directory)
    make_dirpath(download_directory)

    options = webdriver.EdgeOptions()
    # options.add_argument(f"user-data-dir={os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default')}") # edge://version
    # https://stackoverflow.com/questions/6509628/how-to-get-http-response-code-using-selenium-webdriver/50932205#50932205
    options.add_argument(f'--remote-debugging-port={port}')
    options.add_argument('--remote-allow-origins=*')
    prefs = {}
    # prefs['profile.default_content_settings.popups'] = 0
    prefs['download.default_directory'] = download_directory
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.ChromiumEdge(options=options)
    driver.get(url)
    return driver


def get_driver_wait(
    url='https://google.com',
    timeout=20,
    download_directory=DEFAULT_DOWNLOAD_DIRPATH,
    port=DEFAULT_CHROME_DEBUG_PORT,
):
    # type: (str, Union[int, float], str, int) -> Tuple[WebDriver, WebDriverWait]
    driver = get_driver(url=url, download_directory=download_directory, port=port)
    wait = WebDriverWait(driver, timeout=timeout)
    return driver, wait


def driver_get_status(driver, url_requested, chrome_port=DEFAULT_CHROME_DEBUG_PORT, timeout=30):
    # type: (WebDriver, str, int, int|float) -> int
    '''
    Description:
        An augmentation of driver.get() which returns a status code!
        WebDriver doesnt properly tell you if driver.get actually gets back a good exit code... wouldnt it be nice if it did?
        # https://stackoverflow.com/questions/6509628/how-to-get-http-response-code-using-selenium-webdriver/50932205#50932205
        # https://websocket-client.readthedocs.io/en/latest/examples.html
        NOTE: this is still not a guarantee that everything has been loaded! Beauty of AJAX after all...
    Arguments:
        chrome_port: int
            default 7654
            if the chromium driver isnt loaded with this port, things go poorly
    Returns:
        int
    '''
    resp = get(f'http://127.0.0.1:{chrome_port}/json', headers={})
    body = resp.json
    webSocketDebuggerUrl = body[0]['webSocketDebuggerUrl']
    url_requested = url_requested.replace('\\', '/')
    if url_requested.endswith('/'):  # sometimes urls end with / which is semantically different, but not intuitively different
        url_requested = url_requested[:-1]
    glbl_dict = {'uri': url_requested, 'requested': False, 'received': False, 'status': -1}  # type: Dict[str, Union[str, int, bool]]

    def on_open(ws):
        ws.send_text(json.dumps({"id": 1, "method": "Network.enable"}).encode('utf-8'))

    def on_message(ws, message):
        mbody = json.loads(message)
        method = mbody.get('method', '')
        params = mbody.get('params', {})
        if method == 'Network.requestWillBeSent':
            request = params.get('request', {})
            documentURL = params.get('documentURL', {})
            url = request.get('url', '')
            if url.endswith('/'):  # sometimes urls end with / which is semantically different, but not intuitively different
                url = url[:-1]
            if documentURL == url_requested and url == url_requested:
                glbl_dict['requested'] = True
                # LOGGER.debug('%s - %s', method, params)
        elif method == 'Network.responseReceived':
            response = params.get('response', {})
            status = response.get('status', -1)
            if not isinstance(status, int):
                LOGGER.error(response)
                raise ValueError('didnt get an int from the response!')
            url = response.get('url', '')
            if url.endswith('/'):  # sometimes urls end with / which is semantically different, but not intuitively different
                url = url[:-1]
            # LOGGER.debug('%s - %s', method, params)
            if url == url_requested:
                glbl_dict['received'] = True
                glbl_dict['status'] = status

    wsa = WebSocketApp(webSocketDebuggerUrl, on_open=on_open, on_message=on_message)
    t = threading.Thread(target=wsa.run_forever, kwargs=dict(reconnect=1))
    t.start()

    start = time.time()
    try:
        driver.get(url_requested)
        status = int(glbl_dict['status'])
        while status == -1:
            time.sleep(0.1)
            status = int(glbl_dict['status'])
            if time.time() - start > timeout:
                LOGGER.debug('timeout %0.2f sec, glbl_dict: %s', timeout, glbl_dict)
                raise TimeoutError(f'waited > {timeout:0.2f} sec for url {url_requested}')
        return status
    finally:
        wsa.keep_running = False


def find_one_element(driver, by, *ids):
    # type: (WebDriver, str, str) -> Tuple[Optional[WebElement], int]
    '''
    Description:
        Given a by type and a bunch of CSS identifiers,
        return the first found element or None if None...

    Example:
        >>> from selenium.webdriver.common.by import By
        >>> find_one_element(driver, By.ID, 'a', 'b', 'c')

    Returns:
        Tuple[Optional[WebElement], int]
            WebElement or None if not found
            index of id or -1 if not found
    '''
    for i, id_ in enumerate(ids):
        try:
            return driver.find_element(by, id_), i
        except NoSuchElementException:
            pass
    return None, -1


def find_one_element_from_groups(driver, *groups, everything=False):
    # type: (WebDriver, Tuple[str, str], bool) -> Tuple[Optional[WebElement], int]
    '''
    Description:
        Provide a few options to look for or ask for everything.

    Example:
        >>> from selenium.webdriver.common.by import By
        >>> find_one_element_from_groups(
        >>>     driver,
        >>>     (By.ID, 'a', 'b', 'c'),
        >>>     (By.CLASS_NAME, 'x', 'y', 'z'),
        >>>     everything=False,
        >>> )

    Arguments:
        everything: bool
            default false
            by default the first found gets returned
            setting high will make sure ALL are found
                if not all found, none are returned
                if all found, 1st is returned
            NOTE: this is not a wait

    Returns:
        Tuple[Optional[WebElement], int]
            WebElement or None if not found
            index of groups or -1 if not found
    '''
    for g, group in enumerate(groups):
        by, ids = group
        if not isinstance(ids, tuple):
            ids = (ids, )
        elements = []
        for id_ in ids:
            try:
                elements.append(driver.find_element(by, id_))
            except NoSuchElementException:
                pass
        if elements:
            if everything:
                if len(elements) == len(group):
                    return (elements[0], g)
            else:
                return (elements[0], g)
    return None, -1


def web_element_getattr(element, attr):
    # type: (WebElement, str) -> str
    '''
    Description:
        Wraps attribute acquire in a Value Error
    Returns:
        str
    '''
    val = element.get_attribute(attr)
    if val is None:
        raise AttributeError(f'WebElement {element} does not have attr {attr!r}')
    return val


def wait_for(wait, by, selector):
    # type: (WebDriverWait, str, str) -> WebElement
    '''
    Description:
        I just hate constantly doing the EC thing
    Returns:
        WebElement
    '''
    return wait.until(EC.presence_of_element_located((by, selector)))


def wait_for_element_or_driver(web_element, by, ident, timeout=10):
    # type: (WebDriverWait|WebDriver, str, str, int|float) -> WebElement
    '''
    Description:
        The usual wait doesnt work on an individual web element, only the whole driver.
        This allows for nesting waits if the DOM is updated in a recursive way.
    Returns:
        WebElement
    '''
    start = time.time()
    while time.time() - start < timeout:
        try:
            return web_element.find_element(by, ident)
        except NoSuchElementException:
            time.sleep(0.5)
    raise TimeoutError(f'timeout of {timeout:0.2f}sec waiting for {by}, {ident}')


def save_page(driver, output_dirpath=DEFAULT_DOWNLOAD_DIRPATH):
    # type: (WebDriver, str) -> Tuple[str, str]
    '''
    Description:
        From the selenium perspective, downloads as much about the web page as it can
        cookies included.
    Returns:
        Tuple[str, str]
            html filepath
            cookies filepath
    '''
    uri = driver.current_url
    uri_leaves = uri.split('?')[0].split('/')
    non_host_leaves = uri_leaves[1:-1]
    uri_leaf = uri_leaves[-1] or 'index'
    html = driver.page_source
    final_output_dirpath = abspath(output_dirpath, *non_host_leaves)
    os.makedirs(final_output_dirpath, exist_ok=True)

    html_filepath = abspath(final_output_dirpath, f'{uri_leaf}.html')
    with open(html_filepath, 'w', encoding='utf-8') as w:
        w.write(html)
    LOGGER.debug('wrote "%s"', html_filepath)

    cookie_list = driver.get_cookies()
    cookie_str = '; '.join(f'{cookie["name"]}={cookie["value"]}' for cookie in cookie_list)
    cookies_filepath = abspath(final_output_dirpath, f'{uri_leaf}.cookies')
    with open(cookies_filepath, 'w', encoding='utf-8') as w:
        json.dump(cookie_list, w, indent=4)
    LOGGER.debug('wrote "%s"', cookies_filepath)

    with open(abspath(final_output_dirpath, f'{uri_leaf}.cookies-txt'), 'w', encoding='utf-8') as w:
        w.write(cookie_str)

    return html_filepath, cookies_filepath


def load_cookies(driver, cookies):
    # type: (WebDriver, List[dict]) -> None
    '''
    Description:
    Returns:
        Tuple[str, str]
            html filepath
            cookies filepath
    '''
    for cookie in cookies:
        driver.add_cookie(cookie)
