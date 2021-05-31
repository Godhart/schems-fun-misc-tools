#@once
from typing import Any, Optional, Sequence, Mapping, List, Dict


class SchemaClassFactory(object):
    @staticmethod
    def from_dict(data: dict, class_mapping: dict) -> object:
        """
        Creates class depending on 'kind' field in data
        :param data: dict with values for members and 'kind' field to determine class. key is member name
        :param class_mapping: sets mapping between 'kind' field value and created class
        :return:
        """
        kind = data.get('kind', None)
        if kind is None:
            # TODO: assertion
            return None
        class_type = class_mapping.get(kind, None)
        if kind is None:
            # TODO: assertion
            return None
        return class_type


class SchemaClassTemplate(object):
#@witheach


#@declare_class

    def __init__(self, data: Optional[Any[None, Dict]] = None):
        """
        :param data: dict with values for members. key is member name
        """
        self.corrupt = True
        if data is None:
            data = {}
        self.from_dict(data)

    def from_dict(self, data: Dict):
        """
        :param data: dict with values for members. key is member name
        :return:
        """
        # TODO: code to verify data against schema using yamale

        #> get fields data, using defaults where necessary
        #> like this:
        #> if member is scalar/list/dict
        #> self.{mebmer_name} = data.get('{mebmer_name}', {default_value})
        #> if member is nested class then
        #> nested_data = data.get('{member_name}', {default_value})
        #> if nested_data != {default_value} and nested_data is not None:
        #>     class_mapping = \{
        #>         {'{class_name_1}': {class_name_1},
        #>         ...
        #>     \}
        #>     self.{member_name} = SchemaClassFactory.from_dict(nested_data, class_mapping)
        #> TODO: a bit complicated for maps and lists of nested classes
        #@members_from_dict
        pass

    def to_dict(self) -> dict:
        """
        :return: dict with member values. key is member name
        """
        result = {}
        if self.corrupt:
            return result

        #> with each member:
        #> if it's scalar or map or list with default value - export nothing
        #> if self.{member_name} != {default_value}:
        #>     result[{member_name}] = self.{member_name}
        #> if it contains nested classes - export their's data
        #> if self.{member_name} is not None:
        #>     result[{member_name}] = self.{member_name}.to_dict(export_defaults)
        #> TODO: a bit complicated for maps and lists of nested classes
        #@members_to_dict

        return result

    def reset_to_default(self, members: Optional[Any[None, List[str]]] = None) -> None:
        """
        Resets specified members to default values
        :param members: members to reset. If None then all members are reset
        :return: None
        """
        #@members_reset_to_default
        pass

    #@members_as_properties
