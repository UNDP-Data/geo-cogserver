
import uvicorn


if __name__ == '__main__':
    uvicorn.run(app='cogserver:app', host="127.0.0.1", port=8001, log_config="src/cogserver/logconf.yaml", reload=True, reload_dirs=['/home/janf/.local/share/virtualenvs/geo-cogserver-Wjrq5VZr/lib/python3.10/site-packages/titiler/', './'] )
