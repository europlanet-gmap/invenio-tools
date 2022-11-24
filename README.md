# InvenioRDM tools

Repository for tools (Python, Bash) and metadata schema around InvenioRDM (https://inveniordm.docs.cern.ch) on the use for the GMAP project (https://europlanet-gmap.eu).

InvenioRDM (or simply _Invenio_) is the Research Data Management (RDM) software used by GMAP for the internal publication of the data packages produced or linked by the project.
Invenio is being used either as an aggregator (for data products of interest) or as an experimental RDM software for formating and publishing planetary spatial data; It is not meant to _substitute_ Zenodo (https://zenodo.org) as a final, DOI certified data repository.

_Why don't we just use Zenodo, instead?_ - you ask. Because (_i_) Zenodo is a general purpose data repository and planetary (spatial) data - in particular geologial maps - have a particular set of metadata that we, at GMAP, understand are relevante to expose; And (_ii_), because we want to define an homogeneous organization of data and metadata when they - the GMAP maps - get into Zenodo. The standardization of such metadata is a process, takes development, tests, and demands a place for testing and homologation.

The files below provide specifics on the relevant topics:

- [`metadata.md`](metadata.md): how GMAP's metadata set conforms to Invenio metadata fields. We also discuss in there, how to map GMAP's parent project, PLANMAP (https://planmap.eu), into Invenio. As well as Astropedia (https://astrogeology.usgs.gov) data products metadata into Invenio. The discussion is not taken individually on each project, but rather an overall meaning of the different but meaningful alike fields should fit into an homogeneous set.

- [`jsonschema.md`](jsonschema.md): discussion about json-schema (https://json-schema.org/), which extends the discussion in `metadata.md` into a formal definition in terms of software and data systems.

- [`invenio-api.md`](invenio-api.md): talks specifically about InvenioRDM's API, the programatic interface to access, publish, edit records.

And in the different directories, Jupyter notebooks and tools implementing the discussions about metadata and examples of data integration workflows;
- [api/](api/): python code base for the notebooks
- [astropedia/](astropedia/): notebooks accessing and processing Astropedia's maps metadata
- [gmap/](gmap/): gmap metadata-format development notes
- [invenio/](invenio/): use of InvenioRDM API
- [zenodo/](zenodo/): use of Zenodo API

> - [adam/](adam/): examples of using ADAM API (should be moved out from here)
