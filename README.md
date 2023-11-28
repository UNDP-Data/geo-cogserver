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
b) creating a release manually using Github




