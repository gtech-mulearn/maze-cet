from enum import Enum


class UserType(Enum):
    PARTICIPANT = 'Participant'
    ADMIN = 'Admin'


class LearningStationType(Enum):
    UI_UX = 'Ui/Ux'
    WEB = 'Web'
    IOT = 'Iot'
    AI_ML = 'Ai/ML'
    BLOCKCHAIN = 'Blockchain'
    AR_VR = 'Ar/Vr'

    @staticmethod
    def get_values():
        return [station.value for station in LearningStationType]


class RewardTypes(Enum):
    VIP_PASS_AR_VR = 'VIP Pass Ar/Vr'
    HAT_MUG = 'Hat/Mug'
    TSHIRT = 'T Shirt'
    HAND_BAND = 'Hand Band'
    SUNGLASS = 'Sunglass'
    LAPTOP_BAG = 'Laptop Bag'
    HOODIES = 'Hoodies'

    @staticmethod
    def get_values():
        return [rewards.value for rewards in RewardTypes]


class RoleTypes(Enum):
    CEO = 'ceo'
    CTO = 'cto'
    COO = 'coo'
    CCO = 'cco'
    CFO = 'cfo'
    CMO = 'cmo'

    @staticmethod
    def get_values():
        return [roles.value for roles in RoleTypes]