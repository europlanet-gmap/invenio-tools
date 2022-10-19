import ipywidgets as widgets

from collections import UserDict
from typing import Any 

class Form(UserDict):
    def __init__(self):
        super().__init__()
        _main = create_main_widgets()
        _other = create_other_widgets()
        self.update(_main)
        self.update(_other)

    def set(self, field:str, value:Any) -> bool:
        NotImplementedError

    def get(self, field:str) -> Any:
        NotImplementedError

    def read_json(self, filename):
        NotImplementedError

    @property 
    def widget(self):
        form_main = widgets.TwoByTwoLayout(
            top_left = widgets.VBox([
                self['title'],
                self['shortname'],
                self['map_type'],
                self['target'],
                self['bbox_lon_widgets'],
                self['bbox_lat_widgets'],
                self['publication_date'],
                self['doi'],
                self['authors_widgets'],
            ])
        )

        form_descr = widgets.Accordion(
            children = [
                widgets.VBox([
                    self['description'],
                    self['aims'],
                    self['units'],
                    self['stratigraphic_info'],
                ]),
                widgets.VBox([
                    self['crs'],
                    self['output_scale']
                ]),
                widgets.VBox([
                    self['ancillary_data'],
                    self['related_products'],
                    self['heritage'],
                    self['extra_data'],
                ]),
                widgets.VBox([
                    self['standards'],
                    self['comments'],
                    self['acknowledge'],
                ])
            ]
        )

        titles = [
            "Map description",
            "Spatial attributes",
            "Ancillary data",
            "Notes"
        ]

        for i,bx in enumerate(form_descr.children):
            form_descr.set_title(i, titles[i])
            
        form_descr.selected_index = None

        app = widgets.AppLayout(
            header = self['gmap_id'],
            center = widgets.VBox([
                form_main,
                form_descr
            ]),
            left_sidebar = None,
            right_sidebar = None,
            footer = None
        )

        return app



class Items(object):

    def __init__(self, item_description="Text field"):
        
        add_btn = widgets.Button(icon="plus")

        def add_input_widget(btn):
            """Create new Text input widget in items"""
            text = widgets.Text(description = item_description)
            del_btn = widgets.Button(icon="trash")
            del_btn.on_click(lambda btn: self.del_item(text.value))

            new_item = widgets.HBox([text, del_btn])
            
            if all(item.children[0].value.strip() for item in self.widget.children if hasattr(item, 'children')):
                self.widget.children = tuple(list(self.widget.children) + [new_item])
            # self.widget.children = tuple(list(items) + [new_item])
            
        add_btn.on_click(add_input_widget)

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
        
    @property
    def widget(self):
        return self._widget
        

def create_main_widgets() -> dict:

    def create_publicationDate_picker():
        from datetime import date
        return widgets.DatePicker(
            value = date.today(),
            description = "Publication date"
            )

    def create_select_mapTypes(map_types):
        return widgets.SelectMultiple(
            options = sorted(map_types.keys()),
            description = "Map type"
            )

    def create_gmapID_readonly(target_wgt, map_type_wgt, shortname_wgt, map_types_map):
        gmap_id = widgets.Text(
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

    
    map_types = {
        "Integrated": "I",
        "Morphologic": "M",
        "Compositional": "C",
        "Digital model": "D",
        "Stratigraphic": "S",
        "Geo-structural": "G",
    }


    d = dict(

        title = widgets.Text(
            description = "Map title",
            continuous_update = False
        ),

        target = widgets.Combobox(
            options = ['Mars', 'Mercury', 'Moon', 'Venus'],
            placeholder = "Choose the planet/satelite",
            description = "Target body",
            continuous_update = False
        ),

        shortname = widgets.Text(
            description = "Shortname",
            continuous_update = False
        ),

        publication_date = create_publicationDate_picker(),

        map_type = create_select_mapTypes(map_types),

        authors_widgets = Items("Author (fullname)").widget,

        bbox_lon_widgets = widgets.VBox([
            widgets.Label("Longitude (west,east) [-180:180]"),
            widgets.VBox([
                widgets.FloatText(description = "West-Lon"),
                widgets.FloatText(description = "East-Lon")
            ])
        ]),

        bbox_lat_widgets = widgets.VBox([
            widgets.Label("Latitude (min,max) [-90:90]"),
            widgets.VBox([
                widgets.FloatText(description = "Min-Lat"),
                widgets.FloatText(description = "Max-Lat")
            ])
        ]),

        # bbox_widgets = widgets.VBox([
        #     bbox_lon_widgets,
        #     bbox_lat_widgets
        # ]),

        doi = widgets.Text(description="DOI")

    )

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

