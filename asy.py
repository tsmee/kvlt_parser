from bs4 import BeautifulSoup
import csv
import asyncio
import aiohttp
from aiofiles.threadpool import open as aioopen

with open('saved_bands.txt', 'rb') as f_bands:
    saved_bands = f_bands.read().splitlines()
count = len(saved_bands)

with open('out4.csv', 'r', encoding='utf-8') as read_obj:
    csv_reader = csv.reader(read_obj, delimiter='|')
    bands = list(map(tuple, csv_reader))


async def fetch(session, url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    async with session.get(url, headers=headers) as resp:
        print(resp.content_length)
        print(resp.headers)
        await resp.content.read()
        if resp.content_type == 'text/html; charset=UTF-8':
            return None
        return await resp.content.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(session, url)


async def save_logo(session, sem, band_name, path, img_url):

    logo = await fetch(session, img_url)
    if logo:
        async with aioopen(path, 'wb') as f_logo:
            await f_logo.write(logo)
        async with aioopen('saved_bands.txt', 'a', encoding='utf-8') as f_saved:
            await f_saved.write(band_name + '\n')
        global count
        count += 1
        print("Saved band " + band_name + ' , total ' + str(count))
    else:
        print('lets do some recursion')
        await save_logo(session, sem, band_name, path, img_url)


async def check_logo(session, sem, band_name, band_url):
    page = await bound_fetch(sem, band_url, session)
    soup = BeautifulSoup(page, 'html.parser')
    link_elem = soup.find(id='logo')
    if link_elem:
        img_url = link_elem.attrs['href']
        suf = ""
        if saved_bands.count(band_name):
            suf = "({})".format(str(saved_bands.count(band_name)))
        logo_path = band_name + suf + '.jpg'
        await save_logo(session, sem, band_name, logo_path, img_url)


async def mass_action(r):
    global bands
    conn = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=conn) as session:
        while bands:
            semaphore = asyncio.Semaphore(3)
            tasks = []

            for i in range(r):
                if bands:
                    band_data = bands.pop(0)
                    task = asyncio.ensure_future(check_logo(session, semaphore, band_data[0], band_data[1]))
                    tasks.append(task)
            responses = asyncio.gather(*tasks)
            await responses




loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(mass_action(3)))