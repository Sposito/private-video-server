import http.client
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from pytube import YouTube
import time

channel_urls = []
with open('canais.txt', 'r') as file:
    for line in file.readlines():
        if line.startswith('*'):
            line = line[1:-1]
            channel_urls.append(f'https://www.youtube.com{line}/videos')




# Remove navigator.webdriver Flag using JavaScript

for url in channel_urls:
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=option)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print(f'Starting new channel: {url}')
    driver.get(url)
    text = driver.page_source

    elements = driver.find_elements(by=By.ID, value='thumbnail')
    links = [elem.get_attribute('href') for elem in elements]

    for link in links:
        timer = time.time()
        if link is None:
            continue

        # TODO: This O(n) but can get better:
        #  make this file ordered an keep track of indices so we can go by a binary search
        vid = YouTube(link)
        print(link)
        vid_id = None
        if 'v=' in link:
            vid_id = link.split('v=')[1]
        elif 'youtube.com/shorts/' in link:
            vid_id = link.split('youtube.com/shorts/')[1]
        else:
            print('ERROR invalid id')
            continue

        uuid = f'{vid.channel_id}\t{vid_id}'
        print(f'Starting the processing of {uuid}')
        with open(f'videos/id_list.txt', 'r') as file:
            flag = False
            for line in file.readlines():
                if uuid in line:
                    flag = flag or True
                    continue
            if flag:
                print(f'{uuid} already saved')
                continue

        stream = vid.streams.get_highest_resolution()
        try:
            stream.download(f'videos/{vid_id}')
        except http.client.IncompleteRead as e:
            print(f'ERROR: {vid_id} failed to complete the stream [IncompleteRead]')
            continue

        print(f'{time.time() - timer} seconds on {uuid}')

        metadata = False
        try:
            with open(f'videos/{vid_id}.json', 'w') as file:
                details = {'title': vid.title, 'description': vid.description, 'keywords': vid.keywords,
                           'length': vid.length, 'author': vid.author, 'channel': vid.channel_id, 'uri': vid.watch_url}
                file.write(json.dumps(details))
                metadata = True
        except Exception as e:
            print(e.with_traceback())

        with open(f'videos/id_list.txt', 'a') as file:
            file.write(f'{uuid} {metadata}\n')
    driver.close()
