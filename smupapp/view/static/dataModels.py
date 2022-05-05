
class UnitData:
    id = ""
    name = ""
    pass

class DateInformation:
    firstValue = ""
    secondValue = ""
    date = ""
    isWeekend = False
    def __init__(self,firstValue = "",secondValue = "", activityData = "", isWeekend = False, disable = False):
        self.firstValue = firstValue
        self.secondValue = secondValue
        self.date = activityData
        self.isWeekend = isWeekend
        self.disable = disable
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
    id_rule = None
    name = ""
    max_value = ""
    pass

class ExcelData():
    docType = None
    averageParam = None
    dominantParam = None
    varianceParam = None
    def __init__(self, docType = 1, \
                 averageParam = 1, \
                 dominantParam = 1, \
                 varianceParam = 1, \
                 maximumParam = 1, \
                 minimumParam = 1, \
                 standardDeviationParam = 1, \
                 typicalRangeOfVolatilityParam = 1, \
                 timeMinParam = 0, \
                 timeRange = None,
                 anonymizationParam = 0,
                 timeMin = None, \
                 timeFrom = None, \
                 timeTo = None, \
                 id_time_range = 1, \
                 rules = None,
                 processData = None,
                 checkedProcessData=None,
                 unitStatistic = None):
        self.docType = docType
        self.averageParam = averageParam
        self.dominantParam = dominantParam
        self.varianceParam = varianceParam
        self.maximumParam = maximumParam
        self.minimumParam = minimumParam
        if timeMinParam == None:
            self.timeMinParam = False
        else:
            self.timeMinParam = True
        self.standardDeviationParam = standardDeviationParam
        self.typicalRangeOfVolatilityParam = typicalRangeOfVolatilityParam
        self.timeMin = timeMin
        self.timeFrom = timeFrom
        self.timeTo = timeTo
        self.timeRange = timeRange
        self.id_time_range = id_time_range
        self.rules = rules
        self.anonymizationParam = anonymizationParam
        self.unitStatistic = unitStatistic
        self.processData = processData
        self.checkedProcessData = checkedProcessData
class ActivityColData():

    pass

class NotificationFilterData():
    ruleName = ""
    userName = ""
    dateFrom = ""
    dateTo = ""
    timeRange = ""
    dataType = ""
    def __init__(self,ruleName = '',userName = '', \
                 timeFrom = '', timeTo = '', timeRange = 'Dowolna', dataType= 'Dowolna', delay=''):
        self.ruleName = ruleName
        self.userName = userName
        self.timeFrom = timeFrom
        self.timeTo = timeTo
        self.timeRange = timeRange
        self.dataType = dataType
        self.delay = delay
    pass

class NotificationData:

    def __init__(self):
        self.status = None
        self.intervals = None
        self.days = None
    def __int__(self, status = None, intervals = None, days = None):
        self.status = status
        self.intervals = intervals
        self.days = days