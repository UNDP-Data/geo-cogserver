# Geohub's COGserver
GeoHub COG server is powering UNDP GeoHub visualization of raster datasets

COG server builds on [titiler](https://github.com/developmentseed/titiler) a customisable dynamic raster tiling.
It contains following components:

- [x] COG tiler - render tiles from COG's
  - [x] create STAC item from COG
- [x] MosaicJSON tiler - create/render MosaicJSON docs 
- [x] STAC tiler - render STAC items
- [ ] Multiband tiler - render heterogenous COGs 

Additionally, **COG server** aims to hold generic and specific [titiler algos](https://devseed.com/titiler/advanced/Algorithms/)
intended to provide a geospatial analytics toolbox

# versioning & realeases

As per [titiler's](https://github.com/developmentseed/titiler) recommendation
COGserver employs the titiler's API to build a customised server and keeps its own versioning
system.

Releases ca be created by:

a) pushing tags
   1. commit your changes in a branch 
       ```bash
            git checkout -b branch_name
            git add .
            git commit -m "a message"
            
       ```
   2. make and merge the branch through a PR
   3. create a local tag and push it to remote
       ```bash
          git tag -a v0.0.1 -m "v0.0.1"
          git push --tag
       ```
   4. potentially delete/overwrite 
       ```bash
          git push --delete origin v0.0.1 #remote
          git tag -d v0.0.1 #local
       ```
# local development

The server's config variables are defined in [.env](.env). To create `.env` file, please copy `env.example` file by using the command of `cp .env.example .env`. By passing this file at runtime to 
docker-compose the server can be started using:

```commandline
 docker-compose --env-file .env up --build
```

[gdal_rio.env](/gdal_rio.env) contains several important environmental variables.
SOme oare related to teh server/fastapi components while other to the
GDAL/rasterio machinery

```commandline
HOST=0.0.0.0
PORT=8000
```
These two variables control the hostname and port number of the local dev server
when started.

The [Dockerfile](/Dockerfile) contains two more environmental variables that control the behavious of the server

```commandline
ENV LOG_LEVEL=info
ENV RELOAD=--reload
```
The **RELOAD** if left empty will result in reloading being turned off which is desirable for production








