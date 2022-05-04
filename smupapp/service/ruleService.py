from smupapp.models import Rule, RuleHasProcess, Activity, RuleHasEmployee
from smupapp.view.static.messagesTexts import MESSAGES_ACTIVITY_IN_RULE_ERROR, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_OPERATION_ERROR
from smupapp.view.static.staticValues import TIMERANGE_DAY, TIMERANGE_WEEK, TIMERANGE_MONTH

#
#   return
#   activity error - 2
#
def deleteRuleById(ruleId):
    rules = Rule.objects.filter(id_rule=ruleId)
    if rules.exists():
        try:
            ruleHasProcessSet = RuleHasProcess.objects.filter(rule_id_rule=rules[0].id_rule)
            if existRuleActivity(rules[0]):
                return False, MESSAGES_ACTIVITY_IN_RULE_ERROR
            for ruleHasProcess in ruleHasProcessSet:
                ruleHasProcess.delete()
            ruleHasEmployeeSet = RuleHasEmployee.objects.filter(rule_id_rule=rules[0].id_rule)
            for ruleHasEmployee in ruleHasEmployeeSet:
                ruleHasEmployee.delete()
            rules[0].delete()
            return True, MESSAGES_OPERATION_SUCCESS
        except:
            return True, MESSAGES_OPERATION_ERROR

def ruleActiveById(ruleId):
    rules = Rule.objects.filter(id_rule=ruleId)
    if rules is not None:
        r = rules[0]
        if r.is_active == 1:
            r.is_active = 0
        else:
            r.is_active = 1
        r.save()
        return True
    else:
        return False

def formatRulesMax(rules):
    for r in rules:
        if r.max_value == None:
            r.max_value = ''
        else:
            if r.data_type.id_data_type == 1:
                strValue = str(r.max_value).split('.')
                if len(strValue[1]) == 1:
                    strValue = strValue[0] + ':0' + strValue[1]
                else:
                    strValue = strValue[0] + ':' + strValue[1]
                r.max_value = strValue
            elif r.data_type.id_data_type == 2:
                r.max_value = int(r.max_value)
    return rules

def existRuleActivity(rule):
    ruleHasProcessSet = RuleHasProcess.objects.filter(rule_id_rule=rule.id_rule)
    for ruleHasProcess in ruleHasProcessSet:
        activities = Activity.objects.filter(rule_has_process_id_rule_has_process=ruleHasProcess.id_rule_has_process)
        if (len(activities) > 0):
            return True
    return False

def getNumberFromDateType(timeRange):
    if timeRange.name == TIMERANGE_DAY:
        return 1
    elif timeRange.name == TIMERANGE_WEEK:
        return 7
    elif timeRange.name == TIMERANGE_MONTH:
        return 27