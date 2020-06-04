# import requests
import asyncio
from multiprocessing import Manager, Process, Queue

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

try:
    import uvloop
except ImportError:
    print("[Warn] no install uvloop package")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


root_url = 'http://konachan.net'
home_url = '{root}/post?page={page}'
img_dir = 'data/origin_imgs/'
download_origin_img = True


class Critical():
    """ 进程临界区上下文管理器 """

    def __init__(self, vars, lock):
        self.lock = lock
        self.vars = vars

    def __enter__(self):
        self.lock.acquire()
        return self.vars

    def __exit__(self, *args):
        self.lock.release()


async def fetch(session, url):
    """ 异步抓取文本 """
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        message = e.message if hasattr(e, 'message') else type(e)
        print("[ERROR] {}".format(message))


async def download(session, url, file_path):
    """ 异步下载二进制文件 """
    try:
        async with session.get(url) as response:
            content = await response.read()
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
    except Exception as e:
        message = e.message if hasattr(e, 'message') else type(e)
        print("[ERROR] {}".format(message))
        return None


async def get_one_page(page, **context):
    """ 抓取一页的图片 """
    url = home_url.format(root=root_url, page=page)
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if html is None:
            return
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a', class_='thumb')
        for link in links:
            url = root_url + link['href']
            html = await fetch(session, url)
            if html is None:
                continue
            soup = BeautifulSoup(html, 'lxml')
            if download_origin_img:
                img_url = soup.find('a', class_='highres-show')['href']
            else:
                img_url = soup.find('img', id='image')['src']
            ext = img_url.split('.')[-1]
            with Critical(context['vars'], context['lock']) as vars:
                num = vars['id']
                vars['id'] += 1
            file_path = f'{img_dir}{num:06d}.{ext}'
            print(f'{page} {file_path}', end='\r')
            await download(session, img_url, file_path)


async def get_page_from_queue(**context):
    """ 单个协程的任务 """
    pages = context['pages']
    while not pages.empty():
        page = pages.get()
        await get_one_page(page, **context)


def process_task(**context):
    """ 单个进程的任务 """
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(
        get_page_from_queue(**context)) for i in range(100)]
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)

# demo
# res = requests.get(home_url.format(root=root_url, page=1))
# soup = BeautifulSoup(res.text, 'html.parser')
# links = soup.find_all('a', class_='thumb')
# for link in links:
#     res = requests.get(root_url + link['href'])
#     soup = BeautifulSoup(res.text, 'html.parser')
#     img_url = soup.find('img', id='image')['src']
#     print(img_url)


if __name__ == '__main__':
    # TODO:
    # 验证多进程的作用
    pages = Queue()
    share_dict = Manager().dict()
    share_lock = Manager().Lock()
    share_dict['id'] = 0
    processes = []
    context = {
        'pages': pages,
        'vars': share_dict,
        'lock': share_lock,
    }
    for i in range(10000):
        pages.put(i)

    for i in range(5):
        p = Process(target=process_task, kwargs=context)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
