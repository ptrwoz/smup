from django.db.models import Q
from django.shortcuts import render, redirect
from smupapp.models import Process
from smupapp.view.auth.auth import authUser
from natsort import natsort
from itertools import repeat
from django.contrib import messages

from smupapp.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS


class ProcessData:
    no = ""
    id = ""
    name = ""
    tip = ""
    def __init__(self,no, id, name, tip):
        self.number = no
        self.id = id
        self.name = name
        self.tip = tip
def initAvailableProcess(processData):
    for p in processData:
        ap = Process.objects.filter(id_mainprocess=p.id_process)
        if  len(ap) == 0:
            p.available = True
        else:
            p.available = False
    return processData

def sortDataByChapterNo(processData):
    idx = []
    processes = []
    for p in processData:
        idx.append(p.number)
    nIdx = natsort.natsorted(idx)
    for i in nIdx:
        processes.append(processData[idx.index(i)])
    return processes, nIdx
def sortDataByOrder(processData):
    idx = []
    processes = []
    for p in processData:
        idx.append(p.order)
    nIdx = natsort.natsorted(idx)
    for i in nIdx:
        processes.append(processData[idx.index(i)])
    return processes, nIdx
def getChapterNoFromProcess(process):
    no = ''
    while True:
        no = no + '.' + str(process.id_number)[::-1]
        process = process.id_mainprocess
        if process == None:
            break;
    return no[::-1]

def initChapterNo(processData):
    id = 0
    for p in processData:
        sp = p
        no = '.' + str(sp.id_number)[::-1]
        sp = sp.id_mainprocess
        while sp is not None:
            no = no + '.' + str(sp.id_number)
            sp = sp.id_mainprocess
        p.number = no[::-1]
        id = id +1
        p.id = id
    return processData

def getRawProcceses(request):
    rawProcesses = []
    processError = False
    for i in range(1, 1000):
        id = request.POST.get('id_' + str(i))
        name = request.POST.get('name_' + str(i))
        tip = request.POST.get('text_' + str(i))
        if id is not None:
            rawProcesses.append(ProcessData(id, str(i), name, tip))
            if len(id) == 0 or len(name) == 0:
                processError = True
    return rawProcesses, (not processError)

def checkChaptersNo(idx):
    try:
        if len(idx) >0 and idx[0]!= '1.':
            return False
        for i in range(len(idx)-1):
            p = idx[i].split('.')[:-1]
            n = idx[i + 1].split('.')[:-1]
            if len(p) == len(n):
                if int(p[-1])+ 1 != int(n[-1]):
                    return False
            elif len(p) < len(n):
                if int(n[-1]) != 1:
                    return False
            elif len(p) > len(n):
                if int(p[len(n)-1]) + 1 != int(n[-1]):
                    return False
        return True
    except:
        return False
def getPrevChapterNo(idx):
    arr = len(idx.split('.')[-2])
    return idx[0:len(idx) - (arr + 1)]

def saveProcess(request, context):
    prs, result = getRawProcceses(request)
    prs, idx2 = sortDataByChapterNo(prs)
    if checkChaptersNo(idx2) == False:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        context['processData'] = prs
        return render(request, 'process/process.html', context)
    if result == False:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        context['processData'] = prs
        return render(request, 'process/process.html', context)
    processes = Process.objects.all()
    processData = initChapterNo(processes)
    #prs, prs_ids = sortDataByChapterNo(processData)
    existId = []#list(repeat(0, len(processData)))
    for i in range(0, len(prs)):
        partner = None
        changeFlag = False
        ii = 0
        for pp in processData:
            pno = getChapterNoFromProcess(pp)
            if (pno == prs[i].number):
                pp.tip = prs[i].tip
                pp.name = prs[i].name
                pp.order = i
                pp.number = prs[i].number
                pp.save()
                changeFlag = True
                existId.append(pp.id_process)
                break
            #elif len(prs[i].number) > 2 and pno == getPrevChapterNo(prs[i].number):
            #    partner = pp
            ii = ii + 1
        if not changeFlag:
            np = Process()
            np.id_number = prs[i].number.split('.')[-2]
            np.tip = prs[i].tip
            np.name = prs[i].name
            np.order = i
            np.number = prs[i].number
            parent = Process.objects.filter(number = getPrevChapterNo(prs[i].number))
            if parent.exists():
                np.id_mainprocess = parent[0]
            else:
                np.id_mainprocess = None
            np.save()
            existId.append(np.id_process)
            processes = Process.objects.all()
        i = i + 1
    processes = Process.objects.filter(~Q(id_process__in=existId)).order_by('-order')
    #for i in range(len(existId)):
    #    if not existId[i]:
    #        processes[i].delete()
    for dp in processes:
        dp.delete()
    messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
    return redirect('process')

def processView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
        # save tree
        if request.method == 'POST':
            return saveProcess(request, context)
        else:
            processData = Process.objects.all().order_by('order')
            #`processData` = initChapterNo(processData)
            #processData, prs = sortDataByChapterNo(processData)
            #processData = initLevelChaptersNo(processData)
            #if checkChaptersNo(processData) == False:
            #    print()
            cId = 1
            for process in processData:
                process.id = cId
                cId += 1
            context['processData'] = processData
            return render(request, 'process/process.html', context)
    else:
        return redirect('home')
