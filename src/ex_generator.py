import numpy as np

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import FieldGroup
from opencmiss.zinc.fieldmodule import Fieldmodule

from opencmiss.utils.zinc.field import create_field_coordinates, find_or_create_field_group
from opencmiss.utils.zinc.general import AbstractNodeDataObject
from opencmiss.utils.zinc.general import create_node as create_zinc_node
from opencmiss.utils.zinc.general import ChangeManager


GROUP_MAPPING = {
    "0": "one",
    "1": "two",
    "2": "three"
}


class EXPoint(AbstractNodeDataObject):

    def __init__(self, x, y, z, c):
        super(EXPoint, self).__init__(['coordinates'])
        self._x = x
        self._y = y
        self._z = z
        self._c = c

    def get(self):
        return [self._x, self._y, self._z, self._c]

    def coordinates(self):
        return [self._x, self._y, self._z]

    def group(self):
        return self._c

    def __repr__(self):
        return f'x="{self._x}" y="{self._y}" z="{self._z}" class="{self._c}"'


def _create_point(pts: np.array) -> EXPoint:
    return EXPoint(float(pts[0]),
                   float(pts[1]),
                   float(pts[2]),
                   int(pts[3]))


def generate(data: np.array, output_file: str) -> None:

    points = []
    for pts in data:
        points.append(_create_point(pts))

    data_set = {}
    for k, v in GROUP_MAPPING.items():
        data_set[GROUP_MAPPING[k]] = [x for x in points if x.group() == int(k)]

    context = Context("Annotated Lung Data")
    region = context.getDefaultRegion()
    field_module = region.getFieldmodule()
    result = create_field_coordinates(field_module)

    for group, points in data_set.items():
        node_identifiers = create_nodes(field_module, points)
        create_group_nodes(field_module, group, node_identifiers, node_set_name='datapoints')
    region.writeFile(output_file)


def create_nodes(field_module: Fieldmodule, embedded_lists: list, node_set_name='datapoints') -> list:
    node_identifiers = []
    for pt in embedded_lists:
        if isinstance(pt, list):
            node_ids = create_nodes(field_module, pt, node_set_name=node_set_name)
            node_identifiers.extend(node_ids)
        else:
            local_node_id = create_zinc_node(field_module, pt, node_set_name=node_set_name)
            node_identifiers.append(local_node_id)

    return node_identifiers


def create_group_nodes(field_module: Fieldmodule, group_name: str, node_ids: list, node_set_name='nodes') -> None:
    with ChangeManager(field_module):
        group = find_or_create_field_group(field_module, name=group_name)
        group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)

        nodeset = field_module.findNodesetByName(node_set_name)
        node_group = group.getFieldNodeGroup(nodeset)
        if not node_group.isValid():
            node_group = group.createFieldNodeGroup(nodeset)

        nodeset_group = node_group.getNodesetGroup()
        for group_node_id in node_ids:
            node = nodeset.findNodeByIdentifier(group_node_id)
            nodeset_group.addNode(node)
