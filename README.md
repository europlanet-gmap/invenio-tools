# InvenioRDM tools

Repository for tools (Python, Bash, etc) around InvenioRDM (Invenio or IRDM, https://inveniordm.docs.cern.ch).

InvenioRDM provides an API the user can use to query, publish or update packages
(see https://inveniordm.docs.cern.ch/reference/rest_api_index/).

Some actions available to the user:
* _drafts_:
  - list (user) drafts
  - create draft
  - delete draft
  - update draft
  - publish draft
  - upload file(s) to draft
  - delete file(s) from draft
* _records_:
  - search records
  - get a draft/record
  - list a draft/record files
  - get file from draft/record
  - edit a (published) record

Invenio provides a large set of metadata attributes associated to records, most of
them are optional. Such attributes are meant to fully specify a _publication_
in more-or-less specific terms according to the attributes given.

The publication attributes may not be sufficient to characterise the data
_content_ being published; For example, if the use of an instrument or the object
targeted are relevant for data discovery, the set of metadata offered by Invenio
records will not directly accommodate those attributes.
In such cases, we should find a compromise and arrange the relevant information
somehow within records' fields.


## InveioRDM metdata

Inveio metadata available thourgh the graphical user interface and is API is
fully described at https://inveniordm.docs.cern.ch/reference/metadata/#metadata.

The metadata fields (mandatory and optional) of our interest are the following:

| **Attribute** | **Attribute description** | **API document field**
| --- | --- | --- |
| Resource type* | The resource type id from the controlled vocabulary. | `resource_type = { id }` |
| Creators* | Person or organization | `creators = [{ person_or_org }]` |
| Title* | Package title | `title` | 
| Publication_date* | Publication date in ISO8601 (eg, `2020-12-31`) | `publication_date` |
| Additional title | Sub/Extra title | `additional_titles = [{ title, type }]` |
| Description | Free HTML**/plain-text description | `description` |
| Rights/Licenses | License name or statement | `rights = [{ id|title }]` |
| Contributors | People or organisations contributing to the work | `contributors = [{ person_or_org, role }]` |
| Subjects | Subject, keyword(s), classification code describing the resource | `sujects = [{ id|subject }]` | 
| Publisher | Name of entity responsible for the publication. This property will be used to formulate the citation. (eg, `GMAP`) | `publisher` |
| Alternate identifiers | Persistent identifiers for the resource (eg, DOI, Bidcode) | `identifiers = [{ identifier, scheme }]` |
| Related works | Related resources used in the work (eg, DOI, Bidcode) | `related_identifiers = [{ identifier, scheme, relation_type, resource_type }]` |
| Locations | GeoJSON geometry locating the map over the target | `locations = { features = { geometry, place }}` |
| Funding | Project/Award funding the work | `funding = [{ funder|award }]` |
| References | List of reference strings | `references = [{ reference }]` |
| Files | List of files (image, tables, documents) content | `files = { enabled, entries, default_preview }` |

> `*` are mandatory fields.
>
> `**` HTML tables are not rendered (as of IRDM v6)



## GMAP metadata

GMAP has its own metadata set (see https://wiki.europlanet-gmap.eu/bin/view/Main/Documentation/Map-wide%20metadata/) that is especially designed for planetary geological maps. It inherits from the Planmap project, and has a lot of overlap with Astropedia's metadata model.

GMAP packages metadata model:

| **Field** | **Field description (and example entries)** |
| --- | --- |
| Map name (GMAP_ID) | Unique package name (`GMAP-{{target-body}}-{{content-type}}-{{region-label}}_{{detail-label}}`) |
| Target body | Name of target body (eg, `Mercury`) |
| Title of map | Map title (eg, `Awesome Geologic Map of the region X`) |
| Bounding box - Min Lat | Minimum latitude in degrees [-90:90) (< Max Lat) |
| Bounding box - Max Lat | Maximum latitude in degrees (-90:90] (> Min Lat) |
| Bounding box - Min Lon | West-most Longitude in degrees [-180:180) (< Max Lon) |
| Bounding box - Max Lon | East-most Longitude in degrees (-180:180] (> Min Lon) |
| Author(s) | Semi-colon separated list of authors |
| Type | Either "draft" or "released" |
| Output scale | Map spatial scale |
| Original Coordinate Reference System | WKT declaring map' CRS |
| Data used | Semi-colon separated list of ancillary, original data used |
| Standards adhered to | Semi-colon list of standards used in the map |
| DOI of companion paper(s) | DOI of linked publication |
| Aims | Reason, goal for this map |
| Short description | Free-text (500 words maximum) describing the map |
| Related products | Other geological maps complementing this one |
| Units Definition (polygon styling) | Units color definition |
| Stratigraphic info | Description of stratigraphic elements in the map |
| Other comments | free-text (notes, errata, warnings) |
| Heritage used | heritage information |
| Link to other data | Links to extenal resources |
| Acknowledgements | Free-text acknowledge |



## Astropedia

Files and code to parse Astropedia's pages and ingest into InvenioRDM (v6).

Content:
* [Notebook](https://github.com/europlanet-gmap/invenio_tools/blob/main/astropedia_product_publishing-html.ipynb) using API for parsing/publishing the (meta)data packages
* [API](https://github.com/europlanet-gmap/invenio_tools/tree/main/api) for parsing the HTML (and XML) pages and publishing using Invenio's REST API
* [Scratch](https://github.com/europlanet-gmap/invenio_tools/tree/main/scratch) directory with notebooks and auxiliary files used during development
