import asyncio
import csv

import aiohttp
from aiofiles.threadpool import open as aioopen
from bs4 import BeautifulSoup

with open('saved_bands.txt', 'rb') as f_bands:
    saved_bands = f_bands.read().splitlines()
count = len(saved_bands)

with open('out4.csv', 'r', encoding='utf-8') as read_obj:
    csv_reader = csv.reader(read_obj, delimiter='|')
    bands = list(map(tuple, csv_reader))


async def fetch(session, url):
    headers ={'authority': 'www.metal-archives.com', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36', 'cookie': '__cfduid=d329291db14d28ff998419f0b55ee220e1595992006; PHPSESSID=4rn2vpibgi7ngft226q2pqv7s3; __utmc=235797405; __utmz=235797405.1595992007.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); phpbb3_qh6oy_u=1; phpbb3_qh6oy_k=; phpbb3_qh6oy_sid=a24b775c7dfa9410fbcc7ff74039885a; __utma=235797405.1086835883.1595992007.1596064171.1596106774.9; __cf_bm=5fa20e3ce539687f4ac2402dc7380bcdbac2138d-1596109392-1800-AZQQP4b+DX84Oi5gddoKqMPOn8vJaUs+nRVyH0sX1FqzRq0pPCv4sEbYucN588SYfHFE08de97itXs697KP757E=; __utmt=1; __utmb=235797405.6.10.1596106774'}
    async with session.get(url, headers=headers) as resp:
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
loop.run_until_complete(asyncio.ensure_future(mass_action(1)))
