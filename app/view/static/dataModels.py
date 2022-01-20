
class UnitData:
    id = ""
    name = ""
    pass

class DateInformation:
    firstValue = ""
    secondValue = ""
    date = ""
    def __init__(self,firstValue = "",secondValue = "", activityData = ""):
        self.firstValue = firstValue
        self.secondValue = secondValue
        self.date = activityData
    pass

class UserData:
    id = ""
    name = ""
    surname = ""
    login = ""
    password = ""
    unit = ""
    role = ""
    pass

class RuleData():
    name = ""
    max = ""
    pass

class ActivityColData():

    pass
