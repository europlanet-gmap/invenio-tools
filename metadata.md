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
| Resource type(*) | CV | The resource type id from the controlled vocabulary. | `resource_type = { id }` |
| Creators(*) | `obj` | Person or organization | `creators = [{ person_or_org }]` |
| Title(*) | text | Package title | `title` | 
| Publication date(*) | ISO8601 | Publication date (eg, `2020-12-31`) | `publication_date` |
| Additional title | text | Sub/Extra title | `additional_titles = [{ title, type }]` |
| Description | text | HTML/plain-text description | `description` |
| Additional descriptions | `obj` | Descriptions for `abstract`, `methods`, `series-information`, `table-of-contents`, `technical-info`, `other` | `additional_descriptions` |
| Rights/Licenses | CV | License name or statement | `rights = [{ id|title }]` |
| Contributors | text | People or organisations contributing to the work | `contributors = [{ person_or_org, role }]` |
| Subjects | text | Subject, keyword(s), classification code describing the resource | `sujects = [{ id|subject }]` | 
| Publisher | text | Name of entity responsible for the publication. This property will be used to formulate the citation. (eg, `GMAP`) | `publisher` |
| Alternate identifiers | text/CV | Persistent identifiers for the resource (eg, DOI, Bidcode) | `identifiers = [{ identifier, scheme }]` |
| Related identifiers | text/CV | Related resources used in the work (eg, DOI, Bidcode) | `related_identifiers = [{ identifier, scheme, relation_type, resource_type }]` |
| Locations | (0-N) | GeoJSON geometry locating the map over the target | `locations = { features = { geometry, place }}` |
| Funding | text | Project/Award funding the work | `funding = [{ funder|award }]` |
| References | text | List of reference strings | `references = [{ reference }]` |
| Files | | List of files (image, tables, documents) content | `files = { enabled, entries, default_preview }` |

> * draft schema: [invenio_draft.schema.json](json_schema/invenio_draft.schema.json)


## GMAP metadata

GMAP has its own metadata set (see https://wiki.europlanet-gmap.eu/bin/view/Main/Documentation/Map-wide%20metadata/) that is especially designed for planetary geological maps. It inherits from the Planmap project, and has a lot of overlap with Astropedia's metadata model.

In the following table, GMAP packages' metadata set:

> - <sup>u1</sup> `src.name` is not a valid UCD1+ (as of version 1.3), the closest UCD (to name a target body) would be `meta.id;src;pos.bodyrc`
> - (?) indicates attributes under revision

| Field | Description | UCD 
|-|-|-
| Map name (GMAP_ID) | Unique package name (`GMAP-{{target-body}}-{{content-type}}-{{region-label}}_{{detail-label}}`) | `meta.id` 
| Target body | Name of target body (eg, `Mercury`) | `src.name`<sup>u1</sup>
| Title of map | Map title (eg, `Awesome Geologic Map of the region X`) | `meta.title`, `pos.bodyrc` 
| Bounding box - Min Lat | Minimum latitude in degrees [-90:90) (< Max Lat) | `pos.bodyrc.lat` 
| Bounding box - Max Lat | Maximum latitude in degrees (-90:90] (> Min Lat) | `pos.bodyrc.lat` 
| Bounding box - Min Lon | West-most Longitude in degrees [-180:180) (< Max Lon) | `pos.bodyrc.lon` 
| Bounding box - Max Lon | East-most Longitude in degrees (-180:180] (> Min Lon) | `pos.bodyrc.lon` 
| Authors | Semi-colon separated list of authors | `meta.id.PI`, `meta.id.CoI` 
| Original Coordinate Reference System | WKT declaring map' CRS | `pos.frame` 
| Data used | Semi-colon separated list of ancillary, original data used | `meta.ref`, `meta.dataset` 
| Standards adhered to | Semi-colon list of standards used in the map | `meta.ref`, `meta.code.qual` 
| DOI of companion paper | DOI of linked publication | `meta.ref.doi` 
| Short description | Free-text (500 words maximum) describing the map | `meta.abstract` 
| Units Definition | Units color definition, polygon styling | `meta.code.class`, `src.morph.type`, `meta.abstract` 
| Stratigraphic info | Description of stratigraphic elements in the map | `meta.code.class`, `meta.abstract` 
| Acknowledgements | Free-text acknowledge | `meta.ref`, `meta.id.assoc` 
||
| (?) Aims | Reason, goal for this map | `meta.note` 
| (?) Heritage used | heritage information | `meta.ref`, `meta.id.parent` 
| (?) Output scale | Map spatial scale | `pos.wcs.scale` 
| (?) Related products | Other geological maps complementing this one | `meta.ref`, `meta.bib` 
| (?) Type | Either "draft" or "released" | `meta.version` 

| _deprecated:_ ||
|-|-
| (?) Other comments | free-text (notes, errata, warnings) 
| (?) Link to other data | Links to extenal resources 


### GMAP-Invenio metadata mapping

To publish GMAP packages through Invenio we have to map the metadata models to represent the attributes properly.

| **InvenioRDM** | **GMAP** | **Tranform** |
| --- | --- | --- |
| Resource type | "GMAP package" | `dataset` |
| Creators | Authors | |
| Title | Title of map | |
| Additional title | Map name (GMAP_ID) | | 
| Publication_date | | `today()` |
| Description | Short description + SEE BELOW | |
| Rights/Licenses | | `cc`|
| Contributors | | |
| Subjects | Aims | | 
| Publisher | | `GMAP` |
| Alternate identifiers | DOI of companion paper | |
| Related works | Related products + Data used + Link to other data | |
| Locations | Bounding box + (place) Target body | |
| Funding | Acknowledgemennts | |
| References | Heritage used + Standards adhered to | |
| Files | _Raster, Vector, Document_ | |

> GMAP unfit fields: "Type", "Output scale", "Original CRS", "Units definition (polygon styling)", "Stratigraphic info", "Other comments"

#### Description

The `Description` field in Invenio has to accommodate all the GMAP attribute the do not fit in IRDM model,
and possibly repeat some (like Target, and Bounding-box) for clarity, besides GMAP's `Short description`. 


## Astropedia

Files and code to parse Astropedia's pages and ingest into InvenioRDM (v6).

Content:
* [Notebook](https://github.com/europlanet-gmap/invenio_tools/blob/main/astropedia_product_publishing-html.ipynb) using API for parsing/publishing the (meta)data packages
* [API](https://github.com/europlanet-gmap/invenio_tools/tree/main/api) for parsing the HTML (and XML) pages and publishing using Invenio's REST API
* [Scratch](https://github.com/europlanet-gmap/invenio_tools/tree/main/scratch) directory with notebooks and auxiliary files used during development
