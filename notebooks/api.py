import json
import requests
from dataclasses import dataclass, asdict


class InvenioRecords:
    """
    Handle results from GET records
    """
    def __init__(self, records_json):
        self._js = records_json
        self._hits = self._js['hits']['hits']
        
    def __len__(self):
        return int(self._js['hits']['total'])
    count = __len__
    
    def __str__(self):
        return json.dumps(self._js, indent=2)
    
    @property
    def records(self):
        return self._hits
    
    @property
    def links(self):
        return self._js['links']
    
    @property
    def aggregations(self):
        return self._js['aggregations']

    
class InvenioClient:
    """
    Client for Invenio(RDM) API
    """
    _scheme = 'https'
    _hostname = 'localhost' #'127.0.0.1:5000'
    _path_api = '/api'
    _token = None

    def __init__(self, hostname:str, token:str=None):
        self._hostname = hostname
        self._token = token

    def read_records(self) -> InvenioRecords:
        """
        Read all records from server, return InvenioResults object
        """
        path_ext = '/records'
        res = self._get(path_ext)
        js = res.json()
        return InvenioRecords(js)
        
    def create_draft(self, payload) -> dict:
        """
        Create draft (see publish_draft() for publishing it)
        """
        assert isinstance(payload, InvenioAstropedia)

        # Create draft
        path_ext = '/records'
        data_record = payload.create_record_payload()
        
        resp_record = self._post(path_ext, json.dumps(data_record))
        
        # Upload files
        draft_id = resp_record.json()['id']
        
        # 1) initialize file key(s)
        #
        path_ext = f'/records/{draft_id}/draft/files'
        data_files = payload.create_files_payload()
        
        if data_files:
            resp_files = self._post(path_ext, json.dumps(data_files))
            # print("Declare files:", resp_files.json())

            # 2) push files data
            #
            for obj in data_files:
                key = obj['key']
                # push data
                path_ext = f"/records/{draft_id}/draft/files/{key}/content"
                data = payload.read_file(key)
                resp_file = self._put(path_ext, data)
                # print(f"Pushed file {key}", resp_file.json())
                # commit
                path_ext = f"/records/{draft_id}/draft/files/{key}/commit"
                resp_commit = self._post(path_ext, None)
                # print(f"Commit file {key}", resp_commit.json())
                data = None

        # End) let's read what's in there now
        path_ext = f"/records/{draft_id}/draft"
        res = self._get(path_ext)
        return res.json()
            
    def publish_draft(self, draft_id):
        """
        Publish a previously created draft (see create_record())
        """
        path_ext = f"/records/{draft_id}/draft/actions/publish"
        res = self._post(path_ext)
        js = res.json()
        return js
    
    def delete_draft(self, draft_id):
        """
        Delete draft
        """
        path_ext = f"/records/{draft_id}/draft"
        res = self._delete(path_ext)
        js = res.json()
        return js

    def _url(self, path_ext=''):
        path = self._path_api + path_ext
        return f"{self._scheme}://{self._hostname}{path}"
        
    def _headers(self, content_type:str='application/json'):
        hdr = {'Authorization': f"Bearer {self._token}",
               'Content-Type': content_type}
        return hdr
        
    def _get(self, path_ext, params=None):
        base_url = self._url(path_ext)
        return requests.get(base_url, params=params,
                            headers=self._headers(), verify=False)
    
    def _post(self, path_ext, payload=None):
        base_url = self._url(path_ext)
        return requests.post(base_url, data=payload, 
                             headers=self._headers(), verify=False)
    
    def _put(self, path_ext, payload=None):
        content_type:str='application/octet-stream'
        base_url = self._url(path_ext)
        return requests.put(base_url, data=payload, 
                            headers=self._headers(content_type), verify=False)
    
    def _delete(self, path_ext):
        base_url = self._url(path_ext)
        return requests.delete(base_url)



@dataclass
class InvenioAstropedia:
    """
    Formatter from our/astropedia metadata to invenio-rdm records
    """
    title: str
    date_pub: str
    origin: str
    url: str
    description: str
    authors: str
    document_url: str
    status: str
    bounding_box: dict
    scope: str
    browse: str
    product_url: str
    
    _RECORD_TEMPLATE = {
      "access": {
        "record": "public",
        "files": "public"
      },
      "files": {
        "enabled": True
      },
      "metadata": {
      }
    }
    
    def __post_init__(self):
        from os import path
        files = {}
        for f in [self.document_url, self.browse]:
            if f:
                files.update({path.basename(f): f})
        self._files = files
        
    def asdict(self):
        return asdict(self)
    
    to_dict = asdict
    
    def read_file(self, key):
        url = self._files.get(key)
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as err:
            print(f"Request for '{url}' failed, code: {resp.status_code}")
            return None
        
        return resp.content

    def create_files_payload(self):
        """
        Return array of `{'key':<filename>}` objects
        (See https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records
        """
        payload = [] # "entries"
        preview = None
        for key in self._files.keys():
            payload.append({ 'key': key })
        
        return payload
        
    def create_record_payload(self) -> dict:
        """
        Return json data for InvenioRDM record draft
        (See https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records
        """
        def _creators(authors:list, person_or_org:list=None):
            """
            Define list of creators (authors)
            """
            out = []
            person_or_org = person_or_org if person_or_org else ['person']*len(authors)
            for name,p_o in zip(authors,person_or_org):
                if p_o == 'org':
                    crt = {'name': f"{name}", 
                            'type': 'organizational'
                          }
                else:
                    assert p_o == 'person'
                    f_name, g_name = name.split(',')
                    crt = {'family_name': f"{f_name}", 
                            'given_name': f"{g_name}", 
                            'type': 'personal'
                          }
                    
                out.append({'person_or_org': crt})
            return out
        
        def _publication_date(date_string:str):
            from dateutil.parser import isoparse
            return isoparse(date_string).date().isoformat()
        
        def _description(description, **kwargs):
            if kwargs:
                sup_info = "\n<b>Extra:</b>\n"
                sup_info += "<ul>"
                for k,v in kwargs.items():
                    if k == 'bounding_box':
                        _sub = "Bounding-Box:"
                        _sub += "<ul>"
                        _sub += ("<li>"
                                 f"{', '.join(str(k_)+' = '+str(v_) for k_,v_ in v.items())}"
                                 "</li>")
                        _sub += "</ul>"
                    else:
                        _sub = f"{k.title().replace('_',' ')}:"
                        _sub += "<ul>"
                        if isinstance(v, str) and v.startswith('http'):
                            _sub += f"<li><a href='{str(v)}'>{str(v)}</a></li>"
                        else:
                            _sub += f"<li>{str(v)}</li>"
                        _sub += "</ul>"
                    sup_info += f"<li>{_sub}</li>"                
                sup_info += "</ul>"
                description += sup_info
                
            description = (description.replace('<b>', '<p/><b>')
                                      .replace('\n\n', '<br>')
                                      .replace('\n',''))
            return description
        
        def _identifiers(url):
            return [{
                'identifier': url,
                'scheme': 'url'
            }]
                
        payload = self._RECORD_TEMPLATE.copy()
        creators = _creators(self.authors)
        publisher = self.origin
        publication_date = _publication_date(self.date_pub)
        resource_type = {'id': 'dataset'}
        title = self.title
        description = _description(
            description=self.description, 
            bounding_box=self.bounding_box,
            product_page=self.url
        )        
        files = {'enabled': bool(len(self._files))}
        identifiers = _identifiers(url=self.url)
        
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
