import os
import titiler
import jinja2
from fastapi import Request
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

jinja2_env = jinja2.Environment(
    loader=jinja2.ChoiceLoader([jinja2.PackageLoader(__package__, package_path=os.path.join(os.path.dirname(titiler.application.__file__), 'templates'))])
)
templates = Jinja2Templates(env=jinja2_env)




def setup_landing(app=None):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def landing(request: Request):
        """TiTiler landing page."""
        data = {
            "title": "titiler",
            "links": [
                {
                    "title": "Landing page",
                    "href": str(request.url_for("landing")),
                    "type": "text/html",
                    "rel": "self",
                },
                {
                    "title": "the API definition (JSON)",
                    "href": str(request.url_for("openapi")),
                    "type": "application/vnd.oai.openapi+json;version=3.0",
                    "rel": "service-desc",
                },
                {
                    "title": "the API documentation",
                    "href": str(request.url_for("swagger_ui_html")),
                    "type": "text/html",
                    "rel": "service-doc",
                },
                {
                    "title": "TiTiler Documentation (external link)",
                    "href": "https://developmentseed.org/titiler/",
                    "type": "text/html",
                    "rel": "doc",
                },
                {
                    "title": "TiTiler source code (external link)",
                    "href": "https://github.com/developmentseed/titiler",
                    "type": "text/html",
                    "rel": "doc",
                },
            ],
        }

        urlpath = request.url.path
        crumbs = []
        baseurl = str(request.base_url).rstrip("/")

        crumbpath = str(baseurl)
        for crumb in urlpath.split("/"):
            crumbpath = crumbpath.rstrip("/")
            part = crumb
            if part is None or part == "":
                part = "Home"
            crumbpath += f"/{crumb}"
            crumbs.append({"url": crumbpath.rstrip("/"), "part": part.capitalize()})

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "response": data,
                "template": {
                    "api_root": baseurl,
                    "params": request.query_params,
                    "title": "TiTiler",
                },
                "crumbs": crumbs,
                "url": str(request.url),
                "baseurl": baseurl,
                "urlpath": str(request.url.path),
                "urlparams": str(request.url.query),
            },
        )