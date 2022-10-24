import json
import ipywidgets as widgets

from collections import UserDict
from pathlib import Path
from typing import Any, Union

def read_planmap_json(metafile:Union[str,Path]) -> dict:
    """Return JSON object from 'meta_file'"""
    filename = Path(metafile)
    with open(filename) as fp:
        js = json.load(fp)
    return js


def set_data_to_form(json, form):
    for field, value in json.items():
        form.set(field, value)

# layout = [
#     'title',
#     'shortname',
#     'map_type',
#     'target',
#     [
#         {"Longitude (west,east) [-180:180]": ['bbox_lon_west', 'bbox_lon_east']},
#         {"Latitude (min,max) [-90:90]": ['bbox_lat_min', 'bbox_lat_max']}
#     ],
#     'publication_date',
#     'doi',
#     'authors_widgets',
#     [
#         {"Map description": ['description', 'aims', 'units', 'stratigraphic_info']},
#         {"Spatial attributes": ['crs', 'output_scale']},
#         {"Ancillary data": ['ancillary_data', 'related_products', 'heritage', 'extra_data']},
#         {"Notes": ['standards', 'comments', 'acknowledge']}
#     ]
# ]

def assemble_widgets(form, layout):
    """Layout widgets"""
    if isinstance(layout, str):
        return form[layout]

    if isinstance(layout, list):
        return widgets.VBox([ assemble_widgets(form, l) for l in layout ])

    if isinstance(layout, dict):
        _w = []
        for label in layout:
            _w.append(widgets.Label(label))
            _w.append(assemble_widgets(form, layout[label]))
        return widgets.VBox(_w)

    if layout is None:
        return assemble_widgets(form, [ field for field in form ])


class Form(UserDict):
    def __init__(self, json:Union[dict,None] = None, layout:Union[list,None] = None):
        super().__init__()
        _main = create_main_widgets()
        _other = create_other_widgets()
        self.update(_main)
        self.update(_other)
        self._widget = assemble_widgets(self, layout)

    def set(self, field:str, value:Any) -> bool:
        """Set 'value' to 'field'"""
        assert field in self
        wdgt = self[field]
        wdgt.value = value

    def add(self, field:str, value:Any) -> bool:
        NotImplementedError

    def get(self, field:str) -> Any:
        NotImplementedError

    def read_json(self, filename):
        NotImplementedError

    @property 
    def widget(self):
        # form_main = widgets.TwoByTwoLayout(
        #     top_left = widgets.VBox([
        #         self['title'],
        #         self['shortname'],
        #         self['map_type'],
        #         self['target'],
        #         widgets.VBox([
        #             widgets.Label("Longitude (west,east) [-180:180]"),
        #             widgets.VBox([
        #                 self['bbox_lon_west'],
        #                 self['bbox_lon_east']
        #             ])
        #         ]),
        #         widgets.VBox([
        #             widgets.Label("Latitude (min,max) [-90:90]"),
        #             widgets.VBox([
        #                 self['bbox_lat_min'],
        #                 self['bbox_lat_max']
        #             ])
        #         ]),
        #         self['publication_date'],
        #         self['doi'],
        #         self['authors_widgets'],
        #     ])
        # )

        # form_descr = widgets.Accordion(
        #     children = [
        #         widgets.VBox([
        #             self['description'],
        #             self['aims'],
        #             self['units'],
        #             self['stratigraphic_info'],
        #         ]),
        #         widgets.VBox([
        #             self['crs'],
        #             self['output_scale']
        #         ]),
        #         widgets.VBox([
        #             self['ancillary_data'],
        #             self['related_products'],
        #             self['heritage'],
        #             self['extra_data'],
        #         ]),
        #         widgets.VBox([
        #             self['standards'],
        #             self['comments'],
        #             self['acknowledge'],
        #         ])
        #     ]
        # )

        # titles = [
        #     "Map description",
        #     "Spatial attributes",
        #     "Ancillary data",
        #     "Notes"
        # ]

        # for i,bx in enumerate(form_descr.children):
        #     form_descr.set_title(i, titles[i])
            
        # form_descr.selected_index = None

        app = widgets.AppLayout(
            header = self['gmap_id'],
            center = self._widget,
            left_sidebar = None,
            right_sidebar = None,
            footer = None
        )

        return app



class Items(object):

    def __init__(self, description="Text field"):
        self.description = description
        add_btn = widgets.Button(icon="plus")
        add_btn.on_click(lambda btn: self.add_item())
        self._widget = widgets.VBox([add_btn])
        

    def del_item(self, value):
        def not_value(item):
            try:
                found = item.children[0].value == value
            except:
                found = False
            return not found
        
        new_items = filter(not_value, self.widget.children)
        self._widget.children = tuple(new_items)

        return self


    def add_item(self, value=None):
        """Create new Text input widget in items"""
        text = widgets.Text(description = self.description)
        if value is not None:
            text.value = str(value)

        del_btn = widgets.Button(icon="trash")
        del_btn.on_click(lambda btn: self.del_item(text.value))

        new_item = widgets.HBox([text, del_btn])
        
        if all(item.children[0].value.strip() 
                for item in self.widget.children if hasattr(item, 'children')):
            self.widget.children = tuple(list(self.widget.children) + [new_item])

        return self
        
        
    @property
    def widget(self):
        return self._widget

    @property 
    def value(self):
        value = [w[0].value for w in self.widget.children]
        return value 

    @value.setter
    def value(self, value:list):
        for val in value:
            self.add_item(val)
        

widget_types = dict(
    text = widgets.Text,
    float = widgets.FloatText,
    datetime = widgets.DatePicker,
    items_one = widgets.Combobox,
    items_multiple = widgets.SelectMultiple,
)

wt = widget_types


def create_main_widgets() -> dict:
    from datetime import date

    map_types = {
        "Integrated": "I",
        "Morphologic": "M",
        "Compositional": "C",
        "Digital model": "D",
        "Stratigraphic": "S",
        "Geo-structural": "G",
    }

    d = dict(

        title = wt['text'](
            description = "Map title",
            continuous_update = False
        ),

        target = wt['items_one'](
            options = ['Mars', 'Mercury', 'Moon', 'Venus'],
            placeholder = "Choose the planet/satelite",
            description = "Target body",
            continuous_update = False
        ),

        shortname = wt['text'](
            description = "Shortname",
            continuous_update = False
        ),

        publication_date = wt['datetime'](
            value = date.today(),
            description = "Publication date"
        ),

        map_type = wt['items_multiple'](
            options = sorted(map_types.keys()),
            description = "Map type"
        ),

        authors = Items("Author (fullname)").widget,


        bbox_lon_west = wt['float'](description = "West-Lon"),
        bbox_lon_east = wt['float'](description = "East-Lon"),
        bbox_lat_min = wt['float'](description = "Min-Lat"),
        bbox_lat_max = wt['float'](description = "Max-Lat"),

        doi = wt['text'](description="DOI")

    )

    def create_gmapID_readonly(target_wgt, map_type_wgt, shortname_wgt, map_types_map):
        gmap_id = wt['text'](
            description = '<i style="color:gray">GMAP-ID</i>', 
            description_allow_html = True,
            disabled = True
            )

        def on_change_value(change):
            _target = target_wgt.value.strip().title()
            _type = ''.join([map_types_map[t].upper() for t in map_type_wgt.value ])
            _sname = shortname_wgt.value.strip().replace(' ','-').title()
            _id = ["GMAP", _type, _target, _sname]
            if not all(_id):
                # gmap_id.value = "GMAP_<target>_<type>_<shortname>"
                gmap_id.value = ""
            else:
                gmap_id.value = '_'.join(_id)

        target_wgt.observe(on_change_value, names='value')
        shortname_wgt.observe(on_change_value, names='value')
        map_type_wgt.observe(on_change_value, names='value')

        return gmap_id

    d['gmap_id'] = create_gmapID_readonly(
            target_wgt= d['target'],
            map_type_wgt= d['map_type'],
            shortname_wgt= d['shortname'],
            map_types_map= map_types
        )

    return d


def create_other_widgets():

    d = dict(
        description = widgets.Textarea(description="Short description of the map"),
        aims = widgets.Textarea(description="Goal of this map"),
        units = widgets.Textarea(description="Units color definition"),
        stratigraphic_info = widgets.Textarea(description="Map stratigraphic elements"),

        output_scale = widgets.Text(description="Output scale"),
        crs = widgets.Textarea(description="Original CRS"),

        ancillary_data = widgets.Textarea(description="Data used"),
        related_products = widgets.Textarea(description="Related maps"),
        heritage = widgets.Textarea(description="Heritage information"),
        extra_data = widgets.Textarea(description="Links to other data"),

        standards = widgets.Textarea(description="Standards"),
        comments = widgets.Textarea(description="Notes, errata, caveats"),
        acknowledge = widgets.Textarea(description="Acknowledgement"),
    )

    return d

