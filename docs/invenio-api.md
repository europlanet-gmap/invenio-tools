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

