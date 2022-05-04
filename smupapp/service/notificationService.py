from datetime import date
from django.db.models import Q
from smupapp.models import RuleHasProcess, Activity
from smupapp.view.static.dataModels import NotificationData
from smupapp.view.static.messagesTexts import MESSAGES_ACTIVITY_END, MESSAGES_NO_ACTIVITY, MESSAGES_DELAY, \
    MESSAGES_NO_DELAY

def getActivitiesDelay(ruleHasEmployee):
    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule = ruleHasEmployee.rule_id_rule)
    employee = ruleHasEmployee.employee_id_employee
    today = date.today()
    activities = Activity.objects.filter(Q(employee_id_employee = employee) & \
             Q(rule_has_process_id_rule_has_process__in = ruleHasProcess))
    delays = []
    for activity in activities:
        d = activity.time_to - today
        delays.append(d)
    return delays

def addDelay(ruleHasEmployees):
    today = date.today()

    for idx in range(len(ruleHasEmployees)):
        messageData = NotificationData()
        if today > ruleHasEmployees[idx].rule_id_rule.time_to:
            messageData.status = MESSAGES_ACTIVITY_END
            messageData.intervals = ''
            messageData.days = 0
        else:
            no = getActivitiesDelay(ruleHasEmployees[idx])
            if len(no) <= 0:
                messageData.status = MESSAGES_NO_ACTIVITY
                messageData.intervals = ''
                messageData.days = 0
            else:
                minDate = min(no)
                if minDate.days > 0:
                    messageData.status = MESSAGES_NO_DELAY
                    messageData.intervals = ''
                    messageData.days = 0
                else:
                    messageData.status = MESSAGES_DELAY
                    messageData.intervals = ''
                    messageData.days = abs(minDate.days)
        ruleHasEmployees[idx].delay = messageData
    return ruleHasEmployees

def filterByDelay(ruleHasEmployees, gteValue):
    newRuleHasEmployee = []
    for ruleHasEmployee in ruleHasEmployees:
        if ruleHasEmployee.delay.days >= gteValue:
            newRuleHasEmployee.append(ruleHasEmployee)
    return newRuleHasEmployee