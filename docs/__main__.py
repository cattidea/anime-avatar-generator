import os
import asyncio
import aiofiles

from aiohttp import web


try:
    import uvloop
except ImportError:
    print("[Warn] no install uvloop package")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
finally:
    loop = asyncio.get_event_loop()


# routes = web.RouteTableDef()

# @routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")

# @routes.get('%s*' % base)
async def all_handler(request):
    relative_path = request.path.replace(base, '', 1)
    print(relative_path)
    if relative_path == '':
        relative_path = 'index.html'
    file_path = os.path.join(docs_dir, relative_path)
    if not os.path.exists(file_path):
        file_path = os.path.join(docs_dir, '404.html')
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    return web.Response(body=content, headers={'Content-type': 'text/html'})


base = '/docs/'
docs_dir = 'docs/'
host = 'localhost'
port = 8080
app = web.Application()
# app.add_routes(routes)
app.add_routes([web.get('%s{path:.*}' % base, all_handler)])
web.run_app(app, host=host, port=port)
