from django.shortcuts import render, redirect
from app.models import Process
from app.view.auth.auth import authUser

class ProcessData:
    id = ""
    name = ""
    tip = ""
    def __init__(self, id, name, tip):
        self.id = id
        self.name = name
        self.tip = tip

def initChapterNo(processData):
    id = 0
    for p in processData:
        sp = p
        no = '.' + str(sp.idnumber)
        sp = sp.idmainprocess
        while sp is not None:
            no = no + '.' + str(sp.idnumber)
            sp = sp.idmainprocess_id
        p.no = no[::-1]
        id = id +1
        p.id = id
    return processData

'''def getPostData(rawProcessData):
    for i in range(100):
        for j in range(100):
            id = 
            name = request.POST.get('name_1.')'''
def processView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
        # save tree
        if request.method == 'POST':
            rawProcesses = []
            for i in range(1,100):
                id = request.POST.get('id_' + str(i))
                name = request.POST.get('name_' + str(i))
                tip = request.POST.get('text_' + str(i))
                if id is None:
                    break
                else:
                    p = ProcessData(id, name, tip)
                    rawProcesses.append(p)
                    i = i + 1
            return redirect('process')
        else:
            processData = Process.objects.all()
            processData = initChapterNo(processData)
            context['processData'] = processData
            return render(request, 'process/process.html', context)
    else:
        return redirect('home')
