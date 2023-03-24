# const and enum def

import enum


# '''枚举定义'''
class enum_Puzzle_Module(enum.Enum):
    Model_All = 0b1
    Model_Word = 0b10
    Model_LzPinyin = 0b100
    Model_Pinyin = 0b1000
    Model_Multi = 0b10000
    Model_BattleSingle = 0b100000


class enum_Puzzle_Unmatch(enum.Enum):
    Unmatch_All = 0b1
    Unmatch_Word = 0b10
    Unmatch_LzPinyin = 0b100
    Unmatch_Pinyin = 0b1000
    Unmatch_Multi = 0b10000
    Unmatch_BattleSingle = 0b100000


class enumBarButton_Display(enum.Enum):
    Menu_ControlId_All = 0b1
    Menu_ControlId_USER = 0b10
    Menu_ControlId_AI = 0b1000


class enumBarButton_Operate(enum.Enum):
    Menu_ControlId_Work_Auto = 0b1
    Menu_ControlId_Work_Promote = 0b10


class enum_Idiom_Source(enum.Enum):
    ENUM_IDIOM_SOURCE_USER = 0
    ENUM_IDIOM_SOURCE_AI = 1
    ENUM_IDIOM_SOURCE_AUTO = 2


class enum_Init_Type(enum.Enum):
    ENUM_INIT_STARTUP = 0
    ENUM_INIT_RESTART = 1
    ENUM_INIT_CONTINUE = 2


class enum_Idiom_Output(enum.Enum):
    ENUM_IDIOM_OUTPUT_USER = 0
    ENUM_IDIOM_OUTPUT_AI = 1


class enum_Idiom_Type(enum.Enum):
    ENUM_IDIOM_TYPE_USER = 0
    ENUM_IDIOM_TYPE_AI = 1
    ENUM_IDIOM_TYPE_PROMOTE = 2
