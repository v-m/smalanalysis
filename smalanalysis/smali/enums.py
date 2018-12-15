"""This module contains all the enumerations availables in the framework"""

__author__ = "Vincenzo Musco (http://www.vmusco.com)"


from enum import Enum


class Identities(Enum):
    """
    Enumeration defining whose the target of a change or result.
    """
    SELF = 'SELF'
    OTHER = 'OTHER'


class ComparisonIgnores(Enum):
    """
    Enumerations for the type of elements of smali which may be ignores during the comparison
    """
    CLASS_NAME = "CLASS_NAME"
    CLASS_SUPER = "CLASS_SUPER"
    CLASS_IMPLEMENTS = "CLASS_IMPLEMENTS"
    CLASS_METHODS = "CLASS_METHODS"
    CLASS_FIELDS = "CLASS_FIELDS"

    METHOD_PARAMS = "METHOD_PARAMS"
    METHOD_RETURN = "METHOD_RETURN"

    FIELD_NAME = "FIELD_NAME"
    FIELD_TYPE = "FIELD_TYPE"
    FIELD_INIT = "FIELD_INIT"

    WITH_LINES_SOURCECODE = "WITH_LINES_SOURCECODE"
    WITH_LINES_NAME = "WITH_LINES_NAME"

    ANOT_MOD_MODIFIERS = "ANOT_MOD_MODIFIERS"
    ANOT_MOD_ANNOTATIONS = "ANOT_MOD_ANNOTATIONS"


class ChangeTypes(Enum):
    """
    Enumeration containing the coarse nature of a change
    """
    TYPE_CHANGED = 'TYPE_CHANGED'
    NAME_CHANGED = 'NAME_CHANGED'
    NOT_FOUND = 'NOT_FOUND'
    REVISED_METHOD = 'REVISED_METHOD'
    SAME_NAME = 'SAME_NAME'
    FIELD_CHANGED = 'FIELD_CHANGED'
    RENAMED_METHOD = 'RENAMED_METHOD'


class DifferenceType(Enum):
    """
    Enumeration containing the fine nature of a change
    """
    NOT_SAME_NAME = 'NOT_SAME_NAME'
    NOT_SAME_RETURN_TYPE = 'NOT_SAME_RETURN_TYPE'
    NOT_SAME_MODIFIERS = 'NOT_SAME_MODIFIERS'
    NOT_SAME_PARAMETERS = 'NOT_SAME_PARAMETERS'
    NOT_SAME_TYPE = 'NOT_SAME_TYPE'
    NOT_SAME_SOURCECODE_LINES = 'NOT_SAME_SOURCECODE_LINES'
    NOT_SAME_ANNOTATIONS = 'NOT_SAME_ANNOTATIONS'
    NOT_SAME_PARENT = 'NOT_SAME_PARENT'
    NOT_SAME_INIT_VALUE = 'NOT_SAME_INIT_VALUE'
    NOT_SAME_INTERFACES = 'NOT_SAME_INTERFACES'
