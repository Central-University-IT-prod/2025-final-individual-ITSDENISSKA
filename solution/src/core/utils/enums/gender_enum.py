from enum import Enum


class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class ExtendedGenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"
