from django.shortcuts import render, redirect
from smupApp.models import Process
from smupApp.view.auth.auth import authUser
from natsort import natsort
from itertools import repeat
from django.contrib import messages

from smupApp.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS


class ProcessData:
    no = ""
    id = ""
    name = ""
    tip = ""
    def __init__(self,no, id, name, tip):
        self.no = no
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
        idx.append(p.no)
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
        p.no = no[::-1]
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
    existId = list(repeat(0, len(processes)))
    for i in range(0, len(prs)):
        partner = None
        changeFlag = False
        ii = 0
        for pp in processes:
            pno = getChapterNoFromProcess(pp)
            if (pno == prs[i].no):
                pp.tip = prs[i].tip
                pp.name = prs[i].name
                pp.save()
                changeFlag = True
                existId[ii] = 1
                break
            elif len(prs[i].no) > 2 and pno == getPrevChapterNo(prs[i].no):
                partner = pp
            ii = ii + 1
        if not changeFlag:
            np = Process()
            np.id_number = prs[i].no.split('.')[-2]
            np.tip = prs[i].tip
            np.name = prs[i].name
            np.id_mainprocess = partner
            np.save()
            processes = Process.objects.all()
        i = i + 1
    for i in reversed(range(len(existId))):
        if not existId[i]:
            processes[i].delete()
    messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
    return redirect('process')

def processView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
        # save tree
        if request.method == 'POST':
            return saveProcess(request, context)
        else:
            processData = Process.objects.all()
            processData = initChapterNo(processData)
            processData, prs = sortDataByChapterNo(processData)
            #processData = initLevelChaptersNo(processData)
            if checkChaptersNo(prs) == False:
                print()
            context['processData'] = processData
            return render(request, 'process/process.html', context)
    else:
        return redirect('home')
