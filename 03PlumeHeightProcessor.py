#----------Volcanic Lightning Project----------
#Plume altitude record processing script (Grimsvotn)
#Outputs a file containing average recorded heights in bins defined below

#----------
Input1 = "KeflaData.csv"
Input2 = "KlausturData.csv"

Output = "Averages.csv"
EndTime = "2011-05-23 19:00"
TimeFormat = "%Y-%m-%d %H:%M"

StartTime = "2011-05-21 19:00"

TimeBins = True
BinWidth = 30 #minutes
#----------

import csv, numpy
import datetime as d

Values = []

with open(Input1) as F:
    FReader = csv.reader(F)
    for Line in FReader:
        Values.append([d.datetime.strptime(Line[0][:10]+" "+Line[0][11:], TimeFormat),Line[1]])

with open(Input2) as F:
    FReader = csv.reader(F)
    for Line in FReader:
        Values.append([d.datetime.strptime(Line[0][:10]+" "+Line[0][11:], TimeFormat),Line[1]])

Values.sort()
Place = 0
Time = d.datetime.strptime(StartTime, TimeFormat)
TimesList = []
LastTime = d.datetime.strptime(EndTime, TimeFormat)
Interval = d.timedelta(minutes=BinWidth)
MeasTime = Values[0][0]
MeanHeights = []
while Time < LastTime:
    i = 0
    print(MeasTime)
    print(Time + Interval)
    while MeasTime < Time + Interval:
        i += 1
        MeasTime = Values[Place+i][0]
    Heights = []
    for j in range(0,i):
        if float(Values[Place+j][1]) < 1000:
            #1000 seems to indicate no detection
            Heights.append(float(Values[Place+j][1]))
    print(Heights)
    Place = Place + i
    MeanHeights.append(numpy.mean(Heights))
    TimesList.append(Time + (Interval/2))
    Time = Time + Interval
    
print(MeanHeights)
print(TimesList)
print(len(MeanHeights))
print(len(TimesList))

with open(Output, 'w', newline='') as F:
    Writer = csv.writer(F)
    for Pair in zip(MeanHeights, TimesList):
        Writer.writerow(Pair)
