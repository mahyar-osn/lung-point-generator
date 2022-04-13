from opencmiss.zinc.context import Context
from opencmiss.zinc.region import Region
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from opencmiss.zinc.status import OK as RESULT_OK

from opencmiss.utils.zinc.general import ChangeManager


def generate(file_path: str) -> list:
    zinc_context = Context("Digitiser")
    region = zinc_context.getDefaultRegion()
    result = region.readFile(file_path)
    assert result == RESULT_OK, f"Error reading digitised file {file_path}."

    return get_points(region)


def get_points(region: Region) -> list:
    field_module = region.getFieldmodule()
    coordinate_field = field_module.findFieldByName("coordinates")
    with ChangeManager(field_module):
        field_cache = field_module.createFieldcache()
        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        if node_set.getSize() == 0:
            del node_set
            node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        data_array = list()
        node_template = node_set.createNodetemplate()
        node_template.defineField(coordinate_field)
        node_iter = node_set.createNodeiterator()
        node = node_iter.next()
        fe_field = coordinate_field.castFiniteElement()
        while node.isValid():
            node_template.defineFieldFromNode(fe_field, node)
            field_cache.setNode(node)
            result, values = fe_field.getNodeParameters(field_cache, -1, Node.VALUE_LABEL_VALUE, 1, 3)
            assert result == RESULT_OK, "Failed to get coordinates of the data."
            data_array.append(values)
            node = node_iter.next()

    return data_array

