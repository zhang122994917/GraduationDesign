# -*- coding:utf-8 -*-
__author__ = 'Administrator'

#from django.views.decorators.csrf import csrf_exempt
from django.http import Http404,HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import Context
from django.template import Template
from untitled1.wsgi import *
from django import template
import datetime
import MySQLdb
import copy
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def hello(request):
    return HttpResponse("Hello world")

def hours_ahead(request,offset):
    try:
        offset =  int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now()+ datetime.timedelta(hours = offset)
    html = "<html><body>in %s hours(s),it will be %s </body></html>" %(offset,dt)
    return HttpResponse(html)

def dataVisulization(request):
    print None



def chinaMap(request):
    return render_to_response('chinaMap.html')

def addCity(request):
    cityList = request.GET['cityList']
    list = cityList.split(",")

    '''fr = open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\condition.json","r")
    t = fr.read()

    fp =  open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\informativness.json","r")
    tmpArray = fp.read()'''
    a = set(list)
    totalNum,cityDict = citypro1(a)
    conditionDict =  conditionPro(a,totalNum,cityDict,0)
    tempArray=[]
    for k,v in conditionDict.iteritems():
        tempConditionDict =  {}
        tmpString = str(k[0])+","+str(k[1])+","+str(k[2])+","+str(k[3])
        tempConditionDict["name"] = tmpString
        tempConditionDict["value"] = v
        tempArray.append(tempConditionDict)
    def f(a,b):
        return a["value"]>b["value"]
    tArray = sorted(tempArray,key = lambda a:a["value"])
    t = tArray[-15::]
    #json.dump(t,open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\condition.json",'w+'),ensure_ascii=False)
    acceptPro = computeAcceptPro(a,conditionDict)
    rejectPro = computeRejectPro(a,conditionDict)
    informativeness,uniqueness = computeIandU(a,acceptPro,rejectPro)
    tmpArray = []
    for k,v in informativeness.iteritems():
         tempInformativeness = {}
         tmpString = str(k[0])+","+str(k[1])
         tempInformativeness["name"] = tmpString
         tempInformativeness["value"] = v
         tempInformativeness["uniqueness"] = uniqueness[k]
         tempInformativeness["pro"] = cityDict[k]
         tmpArray.append(tempInformativeness)
   # json.dump(tmpArray,open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\informativness.json",'w+'),ensure_ascii=False)
    return render(request,'index.html',{'cityName':json.dumps(cityList,ensure_ascii=False),'condition':json.dumps(t),'informativness':json.dumps(tmpArray)})


def addCondition(request):
    cityName = request.GET['cityName']
    differ = request.GET['time']
    list = cityName.split(',')
    a = set(list)
    totalNum,cityDict = citypro1(a)
    conditionDict =  conditionPro(a,totalNum,cityDict,int(differ))
    tempArray=[]
    for k,v in conditionDict.iteritems():
        tempConditionDict =  {}
        tmpString = str(k[0])+","+str(k[1])+","+str(k[2])+","+str(k[3])
        tempConditionDict["name"] = tmpString
        tempConditionDict["value"] = v
        tempArray.append(tempConditionDict)
    def f(a,b):
        return a["value"]>b["value"]
    tArray = sorted(tempArray,key = lambda a:a["value"])
    t = tArray[-15::]
    #json.dump(t,open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\condition.json",'w+'),ensure_ascii=False)
    acceptPro = computeAcceptPro(a,conditionDict)
    rejectPro = computeRejectPro(a,conditionDict)
    informativeness,uniqueness = computeIandU(a,acceptPro,rejectPro)
    tmpArray = []
    for k,v in informativeness.iteritems():
         tempInformativeness = {}
         tmpString = str(k[0])+","+str(k[1])
         tempInformativeness["name"] = tmpString
         tempInformativeness["value"] = v
         tempInformativeness["uniqueness"] = uniqueness[k]
         tempInformativeness["pro"] = cityDict[k]
         tmpArray.append(tempInformativeness)
   # json.dump(tmpArray,open("C:\Users\Administrator\PycharmProjects\untitled1\static\jsonFile\informativness.json",'w+'),ensure_ascii=False)
    jsonData = json.dumps({'cityName':json.dumps(cityName,ensure_ascii=False),'condition':json.dumps(t,ensure_ascii=False),'informativness':json.dumps(tmpArray,ensure_ascii=False)})
    return HttpResponse(jsonData, content_type="application/json")


