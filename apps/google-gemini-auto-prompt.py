'''
NOT DONE YET AT ALL
worked on between 2026-01-29 and 2026-01-31
'''

import importlib
import re
import os
from chriscarl.core import constants
import chriscarl.core.lib.third.selenium as sel
from chriscarl.core.lib.stdlib.logging import configure_ez

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from chriscarl.core.lib.stdlib import os as cos
from chriscarl.core.lib.stdlib.json import write_json, read_json
from chriscarl.core.lib.stdlib.io import write_text_file

constants.fix_constants(sel)

configure_ez(level='DEBUG')

index_html = cos.abspath(constants.MAIN_TESTS_COLLATERAL_DIRPATH, 'index.html')

constants = importlib.reload(constants)
sel = importlib.reload(sel)
cos = importlib.reload(cos)

download_directory = '~/downloads/gemini'
driver, wait = sel.get_driver_wait(download_directory=download_directory)

# log into google
# log into chatgpt
# log into copilot
# log into claude

while not input('logged into google, chatgpt, copilot, and claude? (y/n)').lower().startswith('y'):
    pass

import time


def gemini_wait_for_prompt_entry():
    full_prompt_area = sel.wait_for(wait, By.XPATH, '//div[@data-node-type="input-area"]')
    return full_prompt_area


def gemini_switch_model_type(model_type='thinking'):
    full_prompt_area = gemini_wait_for_prompt_entry()

    # model_selection_button = driver.find_element(By.XPATH, '//div[@data-node-type="input-area"]/button[@mat-button]')
    down_arrow = full_prompt_area.find_element(By.XPATH, '//mat-icon[@data-mat-icon-name="keyboard_arrow_down"]')
    down_arrow.click()
    # options = sel.wait_for(wait, By.TAG_NAME, 'mat-action-list')
    options = sel.wait_for(wait, By.CLASS_NAME, 'mat-mdc-menu-content')
    buttons = {button.text.lower().splitlines()[0]: button for button in optionsel.find_elements(By.TAG_NAME, 'button')}
    model_type = buttons[model_type]
    model_type.click()

    return full_prompt_area


def prompt_request(prompt_str='Write Python code that prints "hello world" once when run.'):
    textarea = sel.wait_for(wait, By.TAG_NAME, 'rich-textarea')
    prompt = textarea.find_element(By.TAG_NAME, 'div')
    prompt.send_keys(prompt_str)
    prompt.send_keys(Keysel.ENTER)


from chriscarl.core.lib.stdlib import urllib

urllib = importlib.reload(urllib)


def gemini_wait_for_n_prompt_responses(n, timeout=360):
    start = time.time()
    model_responses = []
    while len(model_responses) != n and time.time() - start < timeout:
        try:
            model_responses = driver.find_elements(By.XPATH, '//model-response')
        except Exception:
            time.sleep(1)

    if time.time() - start > timeout:
        raise TimeoutError()
    nth_button_clicked = -1
    response_more_buttons = []
    while len(response_more_buttons) != n and time.time() - start < timeout:
        try:
            response_more_buttons = driver.find_elements(By.XPATH, '//button[@mattooltip="More"]')
            for nth, button in enumerate(response_more_buttons):
                if nth > nth_button_clicked:
                    button.click()  # helps scroll down so to speak
                    nth_button_clicked = nth
                    time.sleep(0.5)
                    body = driver.find_element(By.TAG_NAME, 'body')
                    body.send_keys(Keysel.ESCAPE)
                    time.sleep(0.1)
                    body.send_keys(Keysel.ESCAPE)
        except Exception:
            time.sleep(1)

    if time.time() - start > timeout:
        raise TimeoutError()


REGEX_HTML_ATTRIBUTE = re.compile(r'''\s*(?P<key>(?:(?!href|src|style|alt)\b)[A-Za-z\d_-]+)\s*=\s*["'](?P<value>.*?)["']\s*''')


def clean_html(html):
    html = re.sub(r'\s*\<\!--.*?--\>\s*', '', html, flags=re.MULTILINE | re.DOTALL)
    html = re.sub(r'\<button.*?>(.+?)<\/button\>', r'\g<1>', html, flags=re.MULTILINE | re.DOTALL)
    html = re.sub(r'<[^>\/]+><\/[^>]+>', '', html, flags=re.MULTILINE | re.DOTALL)
    html = re.sub(r'<[^>\/]+><\/[^>]+>', '', html, flags=re.MULTILINE | re.DOTALL)
    html = REGEX_HTML_ATTRIBUTE.sub(' ', html)
    html = re.sub(r' {2,}', ' ', html)
    html = re.sub(r' {1,}>', r'>', html)
    return html


def gemini_collect_n_responses(n, download_dirpath=download_directory, close_after=False):
    # TODO: download images by pressing on the image and then the download button...
    show_code_buttons = driver.find_elements(By.XPATH, '//button[@data-test-id="toggle-code-button"]')
    for show_code_button in show_code_buttons:
        show_code_button.click()
        time.sleep(1)

    model_thoughtses = driver.find_elements(By.XPATH, '//button[@data-test-id="thoughts-header-button"]')
    for model_thoughts in model_thoughtses:
        model_thoughtsel.click()
        time.sleep(1)

    responses = []
    try:
        conversation_containers = driver.find_elements(By.XPATH, '//*[contains(@class, "conversation-container")]')
        for c, conversation_container in enumerate(conversation_containers):
            print(f'{c + 1} / {len(conversation_containers)}')
            # conversation_container = conversation_containers[-1]
            user_query = conversation_container.find_element(By.TAG_NAME, 'user-query')
            user_query_html = user_query.get_attribute('innerHTML')
            thinking_and_response = conversation_container.find_elements(By.TAG_NAME, 'message-content')
            if len(thinking_and_response) == 1:
                thinking_html = ''
                response_html = thinking_and_response[0].get_attribute('innerHTML')
            elif len(thinking_and_response) == 2:
                thinking_html = thinking_and_response[0].get_attribute('innerHTML')
                response_html = thinking_and_response[1].get_attribute('innerHTML')
            else:
                raise ValueError('could not find the model thinking and response...')

            response = dict(query=user_query_html, thinking=thinking_html, response=response_html)
            responsesel.append(response)

            image_filepath = ''
            if '<img' in response_html:
                img = conversation_container.find_element(By.TAG_NAME, 'img')
                img_class = img.get_attribute('class')
                if 'licensed-image' in img_class:
                    src = img.get_attribute('src') or ''
                    if src:
                        alt = img.get_attribute('alt') or ''
                        alt = '-'.join(alt.split())
                        image_filepath = cos.abspath(download_dirpath, f'{alt}.jpg')
                        print(image_filepath)
                        image_basename = osel.path.basename(image_filepath)
                        response_html = re.sub(r'src="[^"]+"', f'src="./{image_basename}"', response_html)
                        urllib.download(src, filepath=image_filepath, is_a='file')
                        response['response'] = response_html
                else:
                    # structured_content_container = conversation_container.find_element(By.TAG_NAME, 'structured-content-container')
                    try:
                        img.click()
                        time.sleep(0.5)
                    except Exception:
                        # the click does work, but it also gets intercepted. eitehr way, ok
                        pass

                    close_button = sel.wait_for(wait, By.XPATH, '//button[@aria-label="Close"]')

                    # structured_content_container.click()
                    overlay_container = driver.find_element(By.CLASS_NAME, 'cdk-overlay-container')
                    download_button = overlay_container.find_element(By.TAG_NAME, 'download-generated-image-button')
                    # download_button = overlay_container.find_element(By.XPATH, '//button[@data-test-id="download-generated-image-button"]')
                    download_dirpath = cos.abspath(download_dirpath)
                    download_dirpath_file_count_prev = set(cos.listdir(download_dirpath))
                    download_button.click()
                    download_dirpath_file_count_post = set(cos.listdir(download_dirpath))

                    if download_dirpath_file_count_post == download_dirpath_file_count_prev:
                        image_filepath = cos.wait_for_new_file(download_dirpath, bad_exts=['.crdownload', '.tmp'])
                    else:
                        diff = list(download_dirpath_file_count_post.difference(download_dirpath_file_count_prev))[0]
                        image_filepath = cos.abspath(download_dirpath, diff)

                    print(image_filepath)
                    image_basename = osel.path.basename(image_filepath)
                    response_html = re.sub(r'src="[^"]+"', f'src="./{image_basename}"', response_html)
                    response['response'] = response_html
                    time.sleep(1)
                    close_button = overlay_container.find_element(By.XPATH, '//button[@aria-label="Close"]')
                    close_button.click()

            response['query'] = clean_html(response['query'])
            response['response'] = clean_html(response['response'])
            response['thinking'] = clean_html(response['thinking'])

            response['img'] = image_filepath
            if image_filepath and '<img' not in response['response']:
                basename = osel.path.basename(image_filepath)
                response['response'] += f'\n<img src="./{basename}" alt="{basename}"></img>'

        write_json(cos.abspath(download_dirpath, 'gemini.json'), responses)

        html = []
        for r, response in enumerate(responses):
            for k, v in response.items():
                html.append(f'<h1>{r} - {k}</h1>')
                html.append(v)

        html_render = f'''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
        {"\n\n".join(html)}
        </body>
        </html>'''
        write_text_file(cos.abspath(download_dirpath, 'gemini.html'), html_render)

    finally:
        if close_after:
            try:
                show_code_buttons = driver.find_elements(By.XPATH, '//button[@data-test-id="toggle-code-button"]')
                for show_code_button in show_code_buttons:
                    show_code_button.click()
                    time.sleep(0.1)

                model_thoughtses = driver.find_elements(By.XPATH, '//button[@data-test-id="thoughts-header-button"]')
                for model_thoughts in model_thoughtses:
                    model_thoughtsel.click()
                    time.sleep(0.1)
            except Exception:
                pass

    return responses


import random

topics = ['data science', 'LLMs', 'Python', 'finance', 'education', 'public service', 'the news', 'mathematics', 'philosophy', 'politics', 'fascism']

simple_prompts = []
for _ in range(100):
    second = first = random.choice(topics)
    while first == second:
        second = random.choice(topics)
    simple_promptsel.append(f'What is {first} and how does it relate to {second}?')

harder_prompts = [
    'Create an image that demonstrates this relationship.',
    'How can I explain the above idea to a 5-year old?',
    'What is a recent example of this in the real world?',
    # 'Create 5 study cards that contain vocab words related to this relationship.',  - causes probelms with google workplace
]

driver.get('https://gemini.google.com')

# REALLY doesnt work...
# html_filepath = r'C:\Users\chris\downloads\gemini.google.com\app\c4c3a5a79a03ef81.cookies'
# if not osel.path.isfile(html_filepath):
#     html_filepath, cookies_filepath = sel.save_page(driver)

# cookies = read_json(html_filepath)
# sel.load_cookies(driver, cookies)

gemini_wait_for_prompt_entry()
time.sleep(3 * random.randint(0, 1000) / 1000)

gemini_switch_model_type(model_type='fast')
time.sleep(3 * random.randint(0, 1000) / 1000)

for i in range(2):
    prompt_request(prompt_str=random.choice(simple_prompts))
    time.sleep(3 * random.randint(0, 1000) / 1000)
    gemini_wait_for_n_prompt_responses(i * 2 + 1, timeout=360)

    prompt_request(prompt_str=random.choice(harder_prompts))
    time.sleep(3 * random.randint(0, 1000) / 1000)
    gemini_wait_for_n_prompt_responses(i * 2 + 2, timeout=360)

# existing chats w/ images:
#   - https://gemini.google.com/app/c4c3a5a79a03ef81
#       responses = gemini_collect_n_responses(4, download_dirpath=download_directory, close_after=True)
# latex in the response:
#   - https://gemini.google.com/app/781e84541b8deb98
# show code:
#   - https://gemini.google.com/app/be49a3b06c2f3c85
#       responses = gemini_collect_n_responses(2, download_dirpath=download_directory)

print(responses[-1]['response'])
print(responses[-1]['img'])

# upload button, but I dont have a way to auto-populate the file in the upload...
upload_button = driver.find_element(By.XPATH, '//button[@aria-label="Open upload file menu"]')
upload_button.click()

time.sleep(0.5)

try:
    image_agree_dialog = driver.find_element(By.TAG_NAME, 'upload-image-disclaimer-dialog')
    agree = image_agree_dialog.find_element(By.XPATH, '//button[@data-test-id="upload-image-agree-button"]')
except NoSuchElementException:
    pass

time.sleep(0.5)
upload_files_btn = driver.find_element(By.XPATH, '//button[@data-test-id="local-images-files-uploader-button"]')
upload_files_btn.click()
