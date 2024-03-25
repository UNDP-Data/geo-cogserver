import httpx
import urllib
from urllib.parse import unquote
import json
titiler = 'http://0.0.0.0:8001/cog/statistics?url=https%253A%252F%252Fundpgeohub.blob.core.windows.net%252Fuserdata%252Fa85516c81c0b78d3e89d3f00099b8b15%252Fdatasets%252FDem_Rwanda_10m_allt_20230921150153.tif%252FDem_Rwanda_10m_allt_20230921150153_band1.tif%253Fc3Y9MjAyMy0wOC0wMyZzcz1iJnNydD1vJnNlPTIwMjQtMTAtMjZUMjElM0EwMSUzQTAxWiZzcD1yJnNpZz1FYzJreFBtQnA2NyUyQmdOcUwyWURHOUQxSUJUWEV4RnB4c0tjZkYlMkZpYzlrMCUzRA%253D%253D'
#titiler = 'https://titiler.xyz/cog/info?url=https%253A%252F%252Fundpgeohub.blob.core.windows.net%252Fuserdata%252Fa85516c81c0b78d3e89d3f00099b8b15%252Fdatasets%252FDem_Rwanda_10m_allt_20230921150153.tif%252FDem_Rwanda_10m_allt_20230921150153_band1.tif%253Fc3Y9MjAyMy0wOC0wMyZzcz1iJnNydD1vJnNlPTIwMjQtMTAtMjZUMjElM0EwMSUzQTAxWiZzcD1yJnNpZz1FYzJreFBtQnA2NyUyQmdOcUwyWURHOUQxSUJUWEV4RnB4c0tjZkYlMkZpYzlrMCUzRA%253D%253D'

u = urllib.parse.urlparse(titiler)
qsd = dict(urllib.parse.parse_qsl(u.query))
qsd = {key:urllib.parse.unquote(value) for (key,value) in qsd.items()}
r = httpx.get(f'{u.scheme}://{u.netloc}{u.path}',params=qsd)
d = r.json()
print(json.dumps(d, indent=4))

