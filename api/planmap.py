"""
Planmap packages parser

Example of Planmap README:
```
---
<img src="./document/PM-MAR-MS-Arsinoes.browse.png" width="800"/>

| Field                                                        | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Map name (PM_ID)                                             | PM-MAR-MS-Arsinoes                                           |
| Map version                                                  | 03                                        |
| Target body                                                  | Mars                                                         |
| Title of map                                                 | Geological Map of Arsinoes and Pyrrhae Chaos, Mars           |
| Bounding box - Min Lat                                       | -12                                                          |
| Bounding box - Max Lat                                       | -5.8                                                         |
| Bounding box - Min Lon (0-360)                               | 329.7                                                        |
| Bounding box - Max Lon (0-360)                               | 334.5                                                        |
| Author(s)                                                    | E. Luzzi, A.P. Rossi                                         |
| Type                                                         | Preliminary                                                  |
| Output scale                                                 | 1:3.000.000                                                  |
| Original Coordinate Reference System                         | Projected Coordinate System: Equirectangular Projection: Plate_Carree false_easting: 0.00000000 false_northing: 0.00000000 central_meridian: 0.00000000 Linear Unit: Meter Geographic Coordinate System: GCS_Geographic_Coordinate_System Datum: D_MARS Prime Meridian: Reference Meridian Angular Unit: Degree |
| Data used                                                    | MOLA Elevation Model MEGDR (463 m/pixel)CTX mosaic by MurrayLabCTX DTM (18 m)HiRISE RED (0,25 m/pixel) |
| Standards adhered to                                         | Planmap mapping standards document                           |
| DOI                                                          |                                                              |
| Aims (one sentence)                                          | Morpho-stratigraphic mapping                                 |
| Short description                                            | This map shows the contacts between the disrupted bedrock of the Chaotic terrain Units and the overlying sedimentary units. In addition, it shows the distribution of the graben/fissures and pit chains that are probably related to an intense past of magmatic activity and calderic collapse. In order to better characterize the mineralogical characteristics of the occurring deposits, also spectral analyses were tried out on the only available CRISM cube in the area (still in progress) |
| Related products (cross link to other Planmap products)      |                                                              |
| Units Definition                                             | Post-collapse craters, PCC, 51-160-44Cap Unit, CAP, 182-162-255Light-toned Layered deposits units, LLD, 77-205-255High Thermal Inertia Chaotic terrain, ChH, 227-28-28Knobby Terrain, ChK, 255-127-0Fractured Plains, ChF, 255-238-3 |
| Stratigraphic info (e.g. production function used)           | N/A                                                          |
| Other comments (reviewer comments, notes on post-processing) |                                                              |
| Heritage used                                                | Glotch and Christensen 2005                                  |
| Link to other repositories                                   |                                                              |
| Acknowledgements beyond Planmap                              | N/A                                                          |
```
"""
import os
import json
import lxml
import requests

from os import path
from datetime import date
from dataclasses import dataclass, asdict



def parse_readme_url(url):
    res = requests.get(url)
    readme = res.text

    _url = '/'.join(url.split('/')[:-1])
    _zip = _url.replace('/pub/','/zip/') + '.zip'

    return _parse_readme(readme, _zip)


def parse_readme_file(filename):
    with open(filename, 'r') as fp:
        readme = fp.read()

    _zip = os.path.dirname(filename) + '.zip'
    print(_zip, os.path.exists(_zip))
    return _parse_readme(readme)


def _parse_readme(readme, zip_package=None):

    def _parse_bbox(table):
        """
        Map's bounding-box fields to ours
        """
        _bbox = {
            'min lon': 'westlon',
            'max lon': 'eastlon',
            'min lat': 'minlat',
            'max lat': 'maxlat'
        }

        def match_bbox(field):
            for bf in _bbox:
                if bf in field.lower():
                    return bf

        bbox = {}
        for field, value in table.items():
            if key := match_bbox(field):
                bbox.update({ _bbox[key] : float(value) })

        return bbox


    table = {}
    for line in readme.split('\n'):
        line = line.strip()
        if not line.startswith('|'):
            continue
        k, v = [ o.strip() for o in line.split('|') if o ]
        if k.lower() == 'field' or k.startswith('-'):
            continue
        table.update({ k: v })

    _bbox = _parse_bbox(table)

    # _zip =

    _meta = {
        'name': table['Map name (PM_ID)'],
        'body': table['Target body'],
        'title': table['Title of map'],
        'authors': table['Author(s)'].split(','),
        'description': table['Short description'],
        'publisher': 'Planmap',
        'pub_date': date.today().isoformat(),
        'bounding_box': _bbox,
        'identifiers': {
            # 'url': _url,
            'doi': table['DOI'],
        },
        'files': {
            # 'data': _zip,
        }
    }

    return InvenioPlanmap(**_meta)


@dataclass
class BasePayload:
    """
    Formatter from our/astropedia metadata to invenio-rdm records
    """
    title: str
    authors: list
    pub_date: str
    publisher: str
    description: str
    bounding_box: dict
    name: str = None
    body: str = None
    # identifiers = {'url': 'https://.../path', 'doi': '123.45/6'}
    identifiers: dict = None
    # files = {'browse': 'image.jpg', 'document': 'map.pdf', 'data': None}
    files: dict = None

    def asdict(self):
        return asdict(self)
    to_dict = asdict

    def create_record_payload(self):
        payload = {
            "access": {
                "record": "public",
                "files": "public"
            },
            "files": {
                "enabled": False
            },
            "metadata": {
                'title': "",
                'creators': [],
                'publisher': "",
                'description': "",
                'resource_type': "",
                'publication_date': "",
                # 'identifiers': None,
            },
        }

        return payload


    def create_files_payload(self):
        payload = []
        return payload



class InvenioPlanmap(BasePayload):
    def create_files_payload(self):
        """
        Return array of `{'key':<filename>}` objects
        (See https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records
        """
        payload = super().create_files_payload()
        # payload = [] # "entries"
        preview = None
        for labe,filename in self.files.items():
            payload.append({ 'key': os.path.basename(filename) })

        return payload

    def create_record_payload(self) -> dict:
        """
        Return json data for InvenioRDM record draft
        (See https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records
        """

        def _creators(authors:str):
            """
            Define list of creators (authors)
            """
            import re

            def is_org(name):
                HINTS = ('center','centre','corporation','technology','science')
                return any([ (word in name.lower()) for word in HINTS ])

            out = []
            for name in authors:
                if is_org(name):
                    crt = {'name': f"{name}",
                            'type': 'organizational'
                          }
                else:
                    _name = re.sub('\(.*\)', '', name)
                    _name = _name.split()
                    f_name = _name[-1]
                    g_name = ' '.join(_name[:-1])
                    crt = {'family_name': f"{f_name}",
                            'given_name': f"{g_name}",
                            'type': 'personal'
                          }

                out.append({'person_or_org': crt})
            return out

        def _description(description, **kwargs):
            # description = description.replace('References:', '<b>References:</b>')
            # if kwargs:
            #     sup_info = "\n<b>Extra:</b>\n"
            #     sup_info += "<ul>"
            #     for k,v in kwargs.items():
            #         if k == 'bounding_box':
            #             _sub = "Bounding-Box:"
            #             _sub += "<ul>"
            #             _sub += ("<li>"
            #                      f"{', '.join(str(k_)+' = '+str(v_) for k_,v_ in v.items())}"
            #                      "</li>")
            #             _sub += "</ul>"
            #         else:
            #             _sub = f"{k.title().replace('_',' ')}:"
            #             _sub += "<ul>"
            #             if isinstance(v, str) and v.startswith('http'):
            #                 _sub += f"<li><a href='{str(v)}'>{str(v)}</a></li>"
            #             else:
            #                 _sub += f"<li>{str(v)}</li>"
            #             _sub += "</ul>"
            #         sup_info += f"<li>{_sub}</li>"
            #     sup_info += "</ul>"
            #     description += sup_info
            #
            # description = (description.replace('<b><b>', '<b>')
            #                           .replace('</b></b>', '</b>')
            #                           .replace('<b>', '<p/><b>')
            #                           .replace('\n\n', '<br>')
            #                           .replace('\n',''))
            return description

        def _identifiers(ids):
            out = []
            for k,v in ids.items():
                if v:
                    out.append({ 'scheme': k, 'identifier': v})
            return out

        # payload = self._RECORD_TEMPLATE.copy()
        payload = super().create_record_payload()

        title = self.title
        publisher = self.publisher
        publication_date = self.pub_date
        resource_type = {'id': 'dataset'}

        creators = _creators(self.authors)
        description = _description(
            description=self.description,
            bounding_box=self.bounding_box,
            # product_page=self.url
        )

        files = {'enabled': bool(len(self.files))}
        identifiers = _identifiers(self.identifiers)

        payload.update({
            'metadata': {
                'creators': creators,
                'publisher': publisher,
                'publication_date': publication_date,
                'resource_type': resource_type,
                'title': title,
                'description': description,
                'identifiers': identifiers
            },
            'files': files
        })

        return payload
