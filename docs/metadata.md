# Metadata
[1]: https://inveniordm.docs.cern.ch/reference/metadata/#metadata
[2]: https://schema.datacite.org/meta/kernel-4.3/

InvenioRDM is the chosen data repository software to manage GMAP data, it provides its own set of metadata attributes<sup>[1][1]</sup> that may - or _must_ - be filled for their publication. 

In this document we start describing Invenio interface, then we discuss GMAP packages. There is an addendum from PLANMAP packages. Third, we discuss referencing Astropedia packages through our Invenio instance.

1. [InvenioRDM](#inveniordm-metadata)
2. [GMAP](#gmap-metadata)
3. [Astropedia](#astropedia)


## InvenioRDM metadata

The metadata fields associated to Invenio records is described in details at:
- https://inveniordm.docs.cern.ch/reference/metadata/#metadata;

Invenio metadata schema is aligned to Datacite's version 4.3<sup>[2][2]</sup>.

In the table below, the attributes and their description. 

> - `(*)` mark mandatory fields.
> - `CV` stands for _controlled vocabulary_, a list of values to choose from.
> - `obj` indicates another set of attributes (an object) is used.
> - `text` means a free-text value.
> - `ISO8601` date format: `YYYY-MM-DD`, `YYYY-MM`, `YYYY`.

| Attribute | Cardinality | Description | API document field |
| --- | --- | --- | --- |
| Additional descriptions | (0-N) | Descriptions for `abstract`, `methods`, `series-information`, `table-of-contents`, `technical-info`, `other` | `additional_descriptions` |
| Additional titles | (0-N) | Sub/Extra title | `additional_titles = [{ title, type }]` |
| Alternate identifiers | (0-N) | Persistent identifiers for the resource (eg, DOI, Bidcode) | `identifiers = [{ identifier, scheme }]` |
| Contributors | (0-N) | People or organisations contributing to the work | `contributors = [{ person_or_org, role }]` |
| Creators* | (1-N) | Person or organization | `creators = [{ person_or_org }]` |
| Description | (0-1) | HTML/plain-text description | `description` |
| Formats | (0-N) |
| Funding references | (0-N) | Project/Award funding the work | `funding = [{ funder|award }]` |
| Locations | (0-N) | GeoJSON geometry locating the map over the target | `locations = { features = { geometry, place }}` |
| Publication date* | (1) | Publication date (eg, `2020-12-31`) | `publication_date` |
| Publisher | (0-1) | Name of entity responsible for the publication. This property will be used to formulate the citation. (eg, `GMAP`) | `publisher` |
| References | (0-N) | List of reference strings | `references = [{ reference }]` |
| Related identifiers | (0-N,CV) | Related resources used in the work (eg, DOI, Bidcode) | `related_identifiers = [{ identifier, scheme, relation_type, resource_type }]` |
| Resource type* | (1,CV) | The resource type id from the controlled vocabulary. | `resource_type = { id }` |
| Rights/Licenses | (0-N,CV) | License name or statement | `rights = [{ id|title }]` |
| Subjects | (0-N) | Subject, keyword(s), classification code describing the resource | `sujects = [{ id|subject }]` | 
| Title* | (1) | Package title | `title` | 
| Version | (0-N) |
| <hr/> | <hr/> | <hr/> | <hr/> | 
| Files | (0-N) | List of files (image, tables, documents) content | `files = { enabled, entries, default_preview }` |

> * draft schema: [invenio_draft.schema.json](json_schema/invenio_draft.schema.json)


## GMAP metadata

GMAP has its own metadata set (see https://wiki.europlanet-gmap.eu/bin/view/Main/Documentation/Map-wide%20metadata/) that is especially designed for planetary geological maps. It inherits from the Planmap project, and has a lot of overlap with Astropedia's metadata model.

In the following table, GMAP packages' metadata set:

> - <sup>u1</sup> `src.name` is not a valid UCD1+ (as of version 1.3), the closest UCD (to name a target body) would be `meta.id;src;pos.bodyrc`
> - (?) indicates attributes under revision

| Attribute | Description | UCD 
|-|-|-
| Acknowledgements | Free-text acknowledge | `meta.ref`, `meta.id.assoc` 
| Authors* | Semi-colon separated list of authors | `meta.id.PI`, `meta.id.CoI` 
| Bounding box - Max Lat | Maximum latitude in degrees (-90:90] (> Min Lat) | `pos.bodyrc.lat` 
| Bounding box - Max Lon | East-most Longitude in degrees (-180:180] (> Min Lon) | `pos.bodyrc.lon` 
| Bounding box - Min Lat | Minimum latitude in degrees [-90:90) (< Max Lat) | `pos.bodyrc.lat` 
| Bounding box - Min Lon | West-most Longitude in degrees [-180:180) (< Max Lon) | `pos.bodyrc.lon` 
| DOI of companion paper | DOI of linked publication | `meta.ref.doi` 
| Data used | Semi-colon separated list of ancillary, original data used | `meta.ref`, `meta.dataset` 
| Map name (GMAP_ID)* | Unique package name (`GMAP-{{target-body}}-{{content-type}}-{{region-label}}_{{detail-label}}`) | `meta.id` 
| Original Coordinate Reference System | WKT declaring map' CRS | `pos.frame` 
| Short description* | Free-text (500 words maximum) describing the map | `meta.abstract` 
| Standards adhered to | Semi-colon list of standards used in the map | `meta.ref`, `meta.code.qual` 
| Stratigraphic info | Description of stratigraphic elements in the map | `meta.code.class`, `meta.abstract` 
| Target body* | Name of target body (eg, `Mercury`) | `src.name`<sup>u1</sup>
| Title of map* | Map title (eg, `Awesome Geologic Map of the region X`) | `meta.title`, `pos.bodyrc` 
| Units Definition | Units color definition, polygon styling | `meta.code.class`, `src.morph.type`, `meta.abstract` 
| ? |
| (?) Aims | Reason, goal for this map | `meta.note` 
| (?) Heritage used | heritage information | `meta.ref`, `meta.id.parent` 
| (?) Link to other data | Links to extenal resources 
| (?) Other comments | free-text (notes, errata, warnings) 
| (?) Output scale | Map spatial scale | `pos.wcs.scale` 
| (?) Related products | Other geological maps complementing this one | `meta.ref`, `meta.bib` 
| (?) Type | Either "draft" or "released" | `meta.version` 
| <hr/> | <hr/> | <hr/> | <hr/> | 
| Files<ul><li>`document/`*<li>`raster/`<li>`vector/`</ul> | Documents, raster and vector data. Mandatory: map in PDF format. | (1-N)


### GMAP-Invenio metadata mapping

To publish GMAP packages through Invenio we have to map the metadata models to represent the attributes properly.

| InvenioRDM Attribute | GMAP Attribute | Cardinality | Default value (in Invenio) |
|-|-|-|-
| Additional descriptions | Original CRS<br/>Other comments<br/>Output scale<br/>Stratigraphic info<br/>Target body*<br/>Units definition | (1-N)
| Additional titles | Map name (GMAP_ID)* | (1)
| Alternate identifiers | DOI of companion paper | (0-1)
| Contributors |-|-|-
| Creators* | Authors* | (1-N)
| Description | Short description* | (1)
| Formats |-|-|-
| Funding references | Acknowledgements | (0-N)
| Locations | Bounding box ({Min,Max}-{Lon,Lat}) | (0-1)
| Publication_date* | | (1) |`today()` 
| Publisher | | (0-1) |`GMAP` 
| References | Heritage used<br/>Standards adhered to | (0-N) 
| Related identifiers | Data used<br/>Link to other data<br/>Related products | (0-N) 
| Resource type* | | (1) | `dataset` 
| Rights/Licenses | | (0-N) | `cc`
| Subjects | Aims | (0-1)
| Title* | Title of map* | (1)
| Version | Type | (0-1)
| <hr/> | <hr/> | <hr/> | <hr/> | 
| Files | `meta.json` (this metadata)<br/>`Map.pdf`*<br/>_documents, raster and vector data_<br/> | (1-N) | `meta.json`


#### _Description_ attribute

The `Description` field in Invenio has to accommodate all the GMAP attribute the do not fit in IRDM model,
and possibly repeat some (like Target, and Bounding-box) for clarity, besides GMAP's `Short description`. 


## Astropedia metadata

Similar to the discussion for GMAP, we want to find a suitable set of metadata attribute mappings 
between Astropedia packages and InvenioRDM. The application is slighlty different: Astropedia 
package data are not meant to be replublished in GMAP's Invenio instance, but rather hyperlink
to the original (USGS) publication pages; Nevertheless, the discussion around metadata models is
the same.

Astropedia do not provide a formal definition of their data packages structure,
like [GMAP](https://wiki.europlanet-gmap.eu/bin/view/Main/Documentation/Map-wide%20metadata/),
so we have to extract the model from their pages.

Here are some maps/packages we will use in this exercise:
- [Unified Geologic Map of the Moon, 1:5M, 2020](https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2)
- [Global Geologic Map of Ganymede, SIM3237](https://astrogeology.usgs.gov/search/map/Ganymede/Geology/Ganymede_SIM3237_Database)
- [Mercury 5M GIS Conversion v2](https://astrogeology.usgs.gov/search/map/Mercury/Geology/Mercury_5M_GIS_conversion_v2)
- [Mars 15M Geologic Map GIS Renovation](https://astrogeology.usgs.gov/search/map/Mars/Geology/Mars15MGeologicGISRenovation)
- [Geologic Map of Io, SIM 3168](https://astrogeology.usgs.gov/search/map/Io/Geology/Io_SIM3168_Database)
- [Mercury MESSENGER MDIS Basemap Enhanced Color Global Mosaic 665m](https://astrogeology.usgs.gov/search/map/Mercury/Messenger/Global/Mercury_MESSENGER_MDIS_Basemap_EnhancedColor_Mosaic_Global_665m)
- [Mars Viking Colorized Global Mosaic 232m v2](https://astrogeology.usgs.gov/search/map/Mars/Viking/MDIM21/Mars_Viking_MDIM21_ClrMosaic_global_232m)

Going through those pages we notice the information is fairly regular, 
and the attributes in the table below compose those necessary-and-suficient 
to fit GMAP/Invenio models. Data files and supplementary material are not
of interest here because (_i_) we want to publish a _metapackage_, and (_ii_)
the details and data provision is Astropedia's job.

| Attribute | Description | Section | Comment |
|-|-|-|-|
| Description | Package description | 
| Publisher | Publishing institution |
| Publication Date | Date of publication |
| Modified | Data of (latest) modification | |
| Author | List of authors | | format varies
| Originator/Group | Institution providing the data? | | clarify
| Purpose | Package goal/application | General 
| Online Linkage | Data file | General | multiple files? |
| Suplemental Information | Links to other resources | General | comma-sep urls
| System | Planetary system (eg, Mars)| Keywords
| Target | Body (eg, Mars) | Keywords
| Theme | Topics | Keywords
| Mission | Mission(s) | Keywords
| Instrument | Instrument | Keywords
| Search Terms | Keywords | Keywords
| Access Constraints | Data access constraints | Contact and Distribution 
| Use Constraints | Data use constraints | Contact and Distribution 
| Data Status and Quality: * | Data quality reports and processing description | Data Status and Quality
| Geospatial Information: * | Geospatial information (eg, b-box, data type, projection) | Geospatial Information

### Astropedia-Invenio metadata mapping

Files and code to parse Astropedia's pages and ingest into InvenioRDM (v6).

Content:
* [Notebook](https://github.com/europlanet-gmap/invenio_tools/blob/main/astropedia_product_publishing-html.ipynb) using API for parsing/publishing the (meta)data packages
* [API](https://github.com/europlanet-gmap/invenio_tools/tree/main/api) for parsing the HTML (and XML) pages and publishing using Invenio's REST API
* [Scratch](https://github.com/europlanet-gmap/invenio_tools/tree/main/scratch) directory with notebooks and auxiliary files used during development
