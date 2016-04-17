# -*- coding: utf-8 -*-
"""
WSGI config for untitled1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "untitled1.settings")

application = get_wsgi_application()



import os,sys
import MySQLdb
import copy
import json



def fileToMatric(filename):
    fr = open(filename,"r",)
    arrayOfLines = fr.readlines()
    numberOfLine = len(arrayOfLines)
    firstLine = arrayOfLines[0].strip().split(',')
    y = len(arrayOfLines)
    twodarray = []
    index = 0
    for line in arrayOfLines:
        line = line.strip()
        listFromLine = line.split(',')
        twodarray.append(listFromLine)
        index += 1
    return twodarray


def connectToDatabase():
    try:
        conn =  MySQLdb.connect(host='localhost',user='root',passwd='',db='test',port=3306,charset='utf8')
        cur = conn.cursor()
        array = []
        array = fileToMatric("D:/aqi/aqi_aggregate.txt")
        values = []
        for i in range(len(array)):
            temp = array[i];
            haze = int(temp[13])
            newhaze = 0
            if haze >0  and haze < 50:
                newhaze = 0
            elif haze >= 50 and  haze <=100:
                newhaze =1
            elif haze > 100 and haze <=150:
                newhaze = 2
            elif haze >150 and haze <=200:
                newhaze = 3
            elif haze > 200 and haze <=300:
                newhaze = 4
            else:
                newhaze = 5
            newarray = [temp[0],temp[1],temp[2],newhaze,int(temp[5]),int(temp[6])]
            values.append(newarray)
        cur.executemany('insert into aqi_aggregate values(%s,%s,%s,%s,%s,%s)',values)
        conn.commit()
        conn.close()
    except MySQLdb.Error,e:
         print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def cityPro():
    try:
        conn = MySQLdb.connect(host="localhost",user='root',passwd='',db='test',port=3306,charset="utf8")
        cur =  conn.cursor()
        number = cur.execute("select * from aqi_aggregate")
        tmp = cur.execute("select * from aqi_aggregate GROUP BY city")
        results = cur.fetchall()
        cityDict = {}
        for r in results:
            cityNumber = cur.execute("select * from aqi_aggregate where city= '%s'" % r[0])
            print float(cityNumber) / number
            cityDict[r[0]] = float(cityNumber / number)
        print cityDict

    except MySQLdb.Error,e:
        print "Mysql Error %s:%s" %(e.args[0],e.args[1])


def citypro1(cityset):
    try:
        conn = MySQLdb.connect(host="localhost",user='root',passwd='',db='test',port=3306,charset="utf8")
        cur =  conn.cursor()
        cityset = set(cityset)
        totalNum = 0
        cityDict={}
        for city in cityset:
            num = cur.execute("select * from aqi_aggregate where city = '%s'" %city )
            totalNum += num
        totalNum = totalNum / 3
        for city in cityset:
            for i in range(6):
                num = cur.execute("select * from aqi_aggregate where city = '%s' and haze = %d " %(city,i))
                pro = float(num) / totalNum
                pro = float('%.3f'%pro)
                cityDict[(city,i)] = pro
        return totalNum,cityDict
    except MySQLdb.Error,e:
        print "Mysql Error %s:%s" %(e.args[0],e.args[1])

def conditionPro(cityset,totalNum,totalSet,differ):
     try:
        conn = MySQLdb.connect(host="localhost",user='root',passwd='',db='test',port=3306,charset="utf8")
        cur =  conn.cursor()
        cityset = set(cityset)
        conditioncityDict ={}
        for city in cityset:
            currentSet = copy.deepcopy(cityset)
            currentSet.remove(city)
            for city1 in currentSet:
                for i in range(6):
                    for j in range(6):
                        if differ ==0:
                            conditionNumber =  cur.execute("select * from aqi_aggregate a1,aqi_aggregate a2 where a1.city = '%s' and a2.city ='%s' and a1.`day` = a2.`day` and a1.`hour` = a2.`hour` and a1.haze = %d and  a2.haze = %d" %(city,city1,i,j))
                        else:
                            conditionNumber = cur.execute("select * from aqi_aggregate a1,aqi_aggregate a2 where a1.city = '%s' and a2.city ='%s' and a1.`day`*24+a1.`hour`+%d = a2.`hour` *24+a2.`hour`and a1.haze = %d and  a2.haze = %d" %(city,city1,differ,i,j))
                        if totalSet[(city,i)] == 0:
                            conditioncityDict[(city,city1,i,j)] = 0
                        else:
                            conditioncityDict[(city,city1,i,j)] = '%.3f'%((float(conditionNumber)/totalNum)/totalSet[(city,i)])  #此为在条件为city，雾霾程度为i的条件下，city1雾霾程度为j条件概率
        return conditioncityDict
     except MySQLdb.Error,e:
         print "Mysql Error %s:%s" %(e.args[0],e.args[1])

def computeAcceptPro(cityset,conditioncityDict):
     acceptPro ={}
     for city1 in cityset:
         for j in range(6):
            currenSet = copy.deepcopy(cityset)
            currenSet.remove(city1)
            sumResult = 0
            for city in currenSet:
                 for  i in range(6):
                    sumResult += float(conditioncityDict[(city,city1,i,j)])
            for city2 in currenSet:
                 for i in range(6):
                     if sumResult == 0:
                         acceptPro[((city2,city1,i,j))] = 0
                     else:
                         acceptPro[(city2,city1,i,j)] ='%.3f' %(float(conditioncityDict[city2,city1,i,j])/float(sumResult))
     return acceptPro

def computeRejectPro(cityset,conditioncityDict):
     rejetctPro ={}
     for city in cityset:
         for i in range(6):
             currenSet = copy.deepcopy(cityset)
             currenSet.remove(city)
             sumResult = 0
             for city1 in currenSet:
                 for j in range(6):
                     sumResult  += 1-float(conditioncityDict[(city,city1,i,j)])
             for city2 in currenSet:
                 for j in range(6):
                     rejetctPro[(city,city2,i,j)] = '%.3f '%((1-float(conditioncityDict[city,city2,i,j]))/sumResult)
     return rejetctPro


def computeIandU(cityset,acceptPro,rejectPro):
    informativeness = {}
    uniqueness ={}
    for city in cityset:
        for i in range(6):
            informativeness[(city,i)] = 1
            uniqueness[(city,i)] = 1
    for j in range(8):
        for city in cityset:
            for i in range(6):
                newI =0
                currentSet = copy.deepcopy(cityset)
                currentSet.remove(city)
                for city1 in currentSet:
                    for j in range(6):
                         newI += float(acceptPro[(city,city1,i,j)])*float(uniqueness[(city1,j)])
                informativeness[(city,i)] = newI
        for city in cityset:
            for i in range(6):
                newU = 0
                currentSet = copy.deepcopy(cityset)
                currentSet.remove(city)
                for city1  in currentSet:
                    for j in range(6):
                        newU += float(rejectPro[(city1,city,j,i)])*float(informativeness[city1,j])
                uniqueness[(city,i)] = newU
        sumI =0
        sumU =0
        for city in cityset:
            for i in range(6):
                sumU += float(uniqueness[(city,i)])
                sumI += float(informativeness[(city,i)])
        for city in cityset:
            for i in range(6):
                uniqueness[(city,i)] /= sumU
                informativeness[(city,i)] /= sumI
    return informativeness,uniqueness





