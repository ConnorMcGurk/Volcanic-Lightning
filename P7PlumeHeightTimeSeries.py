#----------Volcanic Lightning Project----------
#Plume altitude plotting script

#Output:
#Figure 1: Plume heights through time (line)
#Figure 2: Histograms of estimated plume height and stroke rate
#Figure 3: Scatter plot of estimated plume height and stroke rate
#Figure 4: Scatter plot of stroke rate and average magnitude
#Figure 5: Scatter plot of plume height and average magnitude
#Printed values:
#   Plume height - Stroke rate correlation
#   No. of points counted in correlation
#   Average magnitude - stroke rate correlation
#   Average magnitude - plume height correlation
#   Correlation between plume height - stroke rate records shifted by a number
#       of time steps which can be defined below

#----------------
InputFile = "Averages.csv"
XTicks = 7
StartDate = "2011-05-21 19:00:00"
EndDate = "2011-05-23 16:00:00"

HeightColour = "blue"
StrokeColour = "red"
ZeroColour = "orange"

ShowTitle = False
Title = "Grímsvötn - Plume Height / Stroke Rate Time Series"

ShowLabel = False
DP = 5
#Number of decimal places to round line label values to

TestShifts = [-2,-1,0,1,2]
#Shift height time series by these numbers of steps
FontSize = 18

ShowStrokes = True

OverwriteLabels = True
FixLabels = ["21st 19:15","22nd 02:40","22nd 10:05","22nd 17:30","23rd 00:55","23rd 08:20","23rd 15:45"]
#----------------

import csv, sqlite3, numpy, statistics, math
import matplotlib.pyplot as plt
import datetime as d

Conn = sqlite3.connect('C:\\Users\\Connor\\Documents\\Project\\Grimsvotn\\Data.db')
C = Conn.cursor()

#This section to produce matching time interval bins--
TimeFormat = "%Y-%m-%d %H:%M"
BinStartTime = "2011-05-21 19:00"
BinWidth = 30
BinEndTime = "2011-05-23 16:00"

d1 = d.datetime.strptime(BinStartTime, TimeFormat)
d2 = d.datetime.strptime(BinEndTime, TimeFormat)
Interval = d.timedelta(minutes=BinWidth)

BinBounds = []

for i in range(0,int((d2-d1)/Interval)):
    BinBounds.append(d.datetime.strftime(d1 + Interval * i, TimeFormat))

BinBounds.append(d2)

#----------------------------------------------------

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

Dates = []
Heights = []
Start = JulianDay(StartDate)
End = JulianDay(EndDate)

with open(InputFile) as F:
    FReader = csv.reader(F)
    for Line in FReader:
        if JulianDay(Line[1]) >= Start and JulianDay(Line[1]) <= End:
            Dates.append(JulianDay(Line[1]))
            Heights.append(float(Line[0]))

Ax1 = plt.axes()
Ax1.plot(Dates,Heights)

#---Fix labels with actual dates---
LabelPoints = [Dates[0]]
Days = Dates[-1] - Dates[0]
LabelPoints = [Dates[0] + (Days/(XTicks-1))*i for i in range(0, XTicks)]
StrLabels = []
if Days < 1:
    for Point in LabelPoints:
        C.execute("SELECT time(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    Ax1.set_xlabel("Time (UTC)")
else:
    for Point in LabelPoints:
        C.execute("SELECT datetime(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    Ax1.set_xlabel("Date (UTC)")
#A.set_xticks(LabelPoints,StrLabels)
Ax1.set_xticks(LabelPoints)
Ax1.set_xticklabels(StrLabels)

BarWidth = 30 / (60*24)
plt.figure()
Ax2 = plt.axes()
HeightBars = Ax2.bar(Dates, Heights, width=BarWidth, color=HeightColour)

#---Fix labels with actual dates---
LabelPoints = [Dates[0]]
Days = Dates[-1] - Dates[0]
LabelPoints = [Dates[0] + (Days/(XTicks-1))*i for i in range(0, XTicks)]
StrLabels = []
if Days < 1:
    for Point in LabelPoints:
        C.execute("SELECT time(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    Ax2.set_xlabel("Time", fontsize=FontSize)
else:
    for Point in LabelPoints:
        C.execute("SELECT datetime(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0][8:16])
    Ax2.set_xlabel("Date", fontsize=FontSize)
#A.set_xticks(LabelPoints,StrLabels)
Ax2.set_xticks(LabelPoints)
if OverwriteLabels:
    Ax2.set_xticklabels(FixLabels)
else:
    Ax2.set_xticklabels(StrLabels)
Ax2.set_xlim(left=JulianDay(StartDate),right=JulianDay(EndDate))

StrokeRates = []
AvgMags = []

for i in range(0, len(BinBounds)-1):
    C.execute("SELECT COUNT(*) FROM Strikes WHERE Date BETWEEN ? AND ?",(BinBounds[i],BinBounds[i+1]))
    Count = C.fetchall()[0][0]
    StrokeRates.append(Count)
    #if Count:
    #    StrokeRates.append(math.log10(Count))
    #else:
    #    StrokeRates.append(0)
    C.execute("SELECT Mag FROM Strikes WHERE Date BETWEEN ? AND ?",(BinBounds[i],BinBounds[i+1]))
    Mags = C.fetchall()
    if len(Mags):
        AvgMags.append(statistics.mean([abs(Mag[0]) for Mag in Mags]))
    else:
        AvgMags.append(0)

Ax3 = Ax2.twinx()
if ShowStrokes:
    RateBars = Ax3.bar(Dates, StrokeRates, width=BarWidth, color=StrokeColour)
Ax3.set_ylim(top=2000)
Ax2.grid(True)

Ax3.set_ylabel("Rate / Strokes per 30min", fontsize=FontSize)
Ax2.set_ylabel("Height / km", fontsize=FontSize)
if ShowStrokes:
    Ax3.legend((HeightBars, RateBars),("Estimated Plume Height","Stroke Rate"), fontsize=FontSize)
Ax2.yaxis.set_tick_params(labelsize=FontSize)
Ax3.yaxis.set_tick_params(labelsize=FontSize)
Ax2.xaxis.set_tick_params(labelsize=FontSize)
Ax3.xaxis.set_tick_params(labelsize=FontSize)
if ShowTitle:
    Ax2.set_title(Title)

CleanRates = []
CleanHeights = []
CleanMags = []
ZeroRates = []
ZeroHeights = []
ZeroMags = []

for i in range(0, len(Heights)):
    if not numpy.isnan(Heights[i]):
        if StrokeRates[i] > 0:
            CleanHeights.append(Heights[i])
            CleanRates.append(StrokeRates[i])
            CleanMags.append(AvgMags[i])
        else:
            ZeroRates.append(StrokeRates[i])
            ZeroHeights.append(Heights[i])
            ZeroMags.append(AvgMags[i])

print("Plume height - Stroke rate correlation:")
print(numpy.corrcoef(CleanHeights, CleanRates))
print("No. of points counted in correlation:")
print(len(CleanRates))

print("Average magnitude - stroke rate correlation:")      
print(numpy.corrcoef(CleanMags, CleanRates))
print("Average magnitude - plume height correlation:")
print(numpy.corrcoef(CleanMags, CleanHeights))

[Gradient, Intercept] = numpy.polyfit(CleanRates,CleanHeights,1)
#print(numpy.polyfit(CleanRates,CleanHeights,1))

plt.figure()
Ax4 = plt.axes()
Ax4.scatter(CleanRates, CleanHeights, c=StrokeColour)
Ax4.scatter(ZeroRates, ZeroHeights, alpha=0.5, c=ZeroColour)
Ax4.set_xlabel("Rate / Strokes per 30min", fontsize=FontSize)
Ax4.set_ylabel("Estimated Plume Height / km", fontsize=FontSize)
Ax4.yaxis.set_tick_params(labelsize=FontSize)
Ax4.xaxis.set_tick_params(labelsize=FontSize)

sxPoints = [min(CleanRates), max(CleanRates)]
syPoints = [sxPoints[i] * Gradient + Intercept for i in range(0, len(sxPoints))]
LineLabel = "y = " + str(round(Intercept, DP)) + " + " + str(round(Gradient, DP)) + "x"
Ax4.plot(sxPoints, syPoints, c=StrokeColour, label=LineLabel)
if ShowLabel:
    Ax4.legend()

plt.figure()
plt.scatter(CleanMags,CleanRates)
plt.ylabel("Stroke Rate")
plt.xlabel("Average magnitude")
plt.figure()
plt.scatter(CleanMags,CleanHeights)
plt.ylabel("Plume Height")
plt.xlabel("Average magnitude")

#plt.figure()
#plt.bar([i for i in range(0, len(AvgMags))],AvgMags)

#---Correlation coefficients for shifted lists---
for Shift in TestShifts:
    if Shift > 0:
        TestRates = StrokeRates[:-Shift]
        TestHeights = Heights[Shift:]
    elif Shift < 0:
        TestRates = StrokeRates[-Shift:]
        TestHeights = Heights[:Shift]
    else:
        TestRates = StrokeRates
        TestHeights = Heights
    CleanRates = []
    CleanHeights = []

    for i in range(0, len(TestHeights)):
        if not numpy.isnan(TestHeights[i]):
            if TestRates[i] > 0:
                CleanHeights.append(TestHeights[i])
                CleanRates.append(TestRates[i])
            else:
                pass
    print("------Time-shifted correlation coefficients------")
    print("No. of time steps shifted by:")
    print(Shift)
    print("Correlation between plume heights shifted by "+str(Shift)+" steps and stroke rate:")
    print(numpy.corrcoef(CleanHeights, CleanRates))
    #print(CleanHeights[:3])
    #print(CleanRates[:3])
    #print(len(CleanRates))   

plt.show()
