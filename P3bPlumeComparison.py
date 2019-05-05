#----------Volcanic Lightning Project----------
#Plume heights and strike records
#Also separates strokes into tables of volcanic and meteorological

#Output:
#Figure 1: Plume height / stroke count scatter plot
#Figure 2: Plume height / stroke magnitude scatter plot
#*2 figures showing plume height, stroke count and average magnitude ordered by height
#*10 figures showing plume height, stroke count and average magnitude by date
#*1 figure showing plume height, stroke count and average magnitude ordered by date (without gaps)
#*These figures can be switched off in the parameters below
#Printed values:
#   Plume height - stroke rate correlation
#   Magnitude - stroke rate correlation
#   Magnitude - plume height correlation
#   No. of plumes counted in above correlations

#---Parameters---
Title = "Shiveluch - Plume Records"

#Coordinates of volcano [Lat,Lon]
Location = [56.653,161.36]

Title = "Plume Heights, Strike Counts and Average Magnitudes"

#File to source plume height record from:
InputFile = "PlumeStrikeAssociation.csv"

RateNumber = 50

RemoveRepetitions = False
FadeRepetitions = True
RemoveResuspended = True

PColour = "black"
LColour = "red"

HeightOrderPlot = True  #Show bars ordered by height
DateBarsPlot = True #Show bars through time
DateBarLimits = ["2013-06-01","2013-12-01","2014-06-01","2014-12-01","2015-06-01","2015-12-01","2016-06-01","2016-12-01","2017-06-01","2017-12-01","2018-02-01"]
XTicks = 6

DOrderedBars = True #Show bars ordered by date

#----------------

import matplotlib.pyplot as plt
import sqlite3, csv, numpy, math

Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

def TakeFirst(elem):
    "Take first element only for sort."
    return elem[0]

Dates = []
PlumeHeights = []
StrikeCounts = []
AvgMagnitudes = []
StrokeRates = []
Alphas = []

try:
    C.execute("DROP TABLE Eruptive2")
except:
    print("Exception.")

try:
    C.execute("DROP TABLE Met2")
except:
    print("Exception.")

C.execute("""CREATE TABLE Eruptive2
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
C.execute("""CREATE TABLE Met2
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
C.execute("""INSERT INTO Met2
SELECT * FROM Strikes""")

with open(InputFile, newline='') as F:
    FReader = csv.reader(F)
    for Line in FReader:
        if Line[0]:
            Remove = False
            Flag = Line[2]
            if RemoveRepetitions:
                if Flag == "1":
                    Remove = True
            if RemoveResuspended:
                if Flag == "2":
                    Remove = True
            if not Remove:
                Date = Line[0]
                FirstRef = Line[4]
                LastRef = Line[5]
                Height = float(Line[3])
                if FirstRef:
                    C.execute("SELECT * FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                    Out = C.fetchall()
                    C.execute("INSERT INTO Eruptive2 SELECT * FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                    C.execute("DELETE FROM Met2 WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                    C.execute("SELECT julianday(Date) FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                    OutDates = C.fetchall()
                else:
                    Out = []
                StrikeCount = len(Out)
                if FadeRepetitions and Flag == "1":
                    Alphas.append(0.5)
                else:
                    Alphas.append(1)
                PeakCurrents = []
                Magnitudes = []
                for i in range(0, StrikeCount):
                    PeakCurrents.append(Out[i][4])
                    Magnitudes.append(abs(Out[i][4]))
                PlumeHeights.append(Height)
                Dates.append(JulianDay(Date))
                if StrikeCount:
                    StrikeCounts.append(StrikeCount)
                    AvgMagnitudes.append(numpy.mean(Magnitudes))
                else:
                    StrikeCounts.append(0)
                    AvgMagnitudes.append(0)
                if StrikeCount > RateNumber:
                    MinTime = OutDates[RateNumber-1][0] - OutDates[0][0]
                    for i in range(0, StrikeCount-RateNumber):
                        if OutDates[i+RateNumber-1][0] - OutDates[i][0] < MinTime:
                            MinTime = OutDates[i+RateNumber-1][0] - OutDates[i][0]
                    Rate = (RateNumber / MinTime) * 1440
                    #StrokeRates.append(Rate)
                    StrokeRates.append(math.log10(Rate))
                else:
                    Rate = 0
                    StrokeRates.append(0)

Nos = [i for i in range(0, len(PlumeHeights))]

X = sorted(PlumeHeights, reverse=True)
Y = [x for _,x in sorted(zip(PlumeHeights,StrikeCounts),key=TakeFirst, reverse=True)]
Z = [x for _,x in sorted(zip(PlumeHeights,AvgMagnitudes),key=TakeFirst, reverse=True)]
A = [x for _,x in sorted(zip(PlumeHeights,StrokeRates),key=TakeFirst, reverse=True)]

#print("Plume height - stroke count correlation:")
#print(numpy.corrcoef(PlumeHeights, StrikeCounts))

m1 = []
p1 = []
c1 = []

for i in range(0, len(StrikeCounts)):
    if StrikeCounts[i] and PlumeHeights[i]:
        c1.append(StrikeCounts[i])
        m1.append(AvgMagnitudes[i])
        p1.append(PlumeHeights[i])

[Gradient, Intercept] = numpy.polyfit(c1,p1,1)
plt.scatter(c1,p1)
axPoints = [0, max(c1)]
ayPoints = [axPoints[i] * Gradient + Intercept for i in range(0, len(axPoints))]
plt.plot(axPoints, ayPoints)
plt.figure()

print("Plume height - stroke rate correlation (excluding zero values):")
print(numpy.corrcoef(c1, p1))

print("Magnitude - stroke rate correlation:")
print(numpy.corrcoef(m1, c1))
plt.scatter(m1, c1)
print("Magnitude - plume height correlation:")
print(numpy.corrcoef(m1, p1))
print("Number of plumes counted:")
print(len(m1))

#p2 = []
#for i in range(0, len(p1)):
#    d = Intercept + Gradient * c1[i]
#    p2.append(p1[i] - d)
#print(numpy.corrcoef(m1,p2))

plt.show()

if HeightOrderPlot:
    Fig1, (a1, a2, a3) = plt.subplots(3, 1, sharex = True)
    a1.bar(Nos[:int(len(Nos)/2)],X[:int(len(Nos)/2)], color=PColour)
    a1.set_ylabel("Max Plume Height/km")
    ymin1, ymax1 = a1.get_ylim()
    a1.set_title("Shiveluch Plumes and Lightning (1/2)")
    a2.bar(Nos[:int(len(Nos)/2)],Y[:int(len(Nos)/2)], color=LColour)
    a2.set_ylabel("Strike count")
    ymin2, ymax2 = a2.get_ylim()
    a3.bar(Nos[:int(len(Nos)/2)],Z[:int(len(Nos)/2)], color=LColour)
    a3.set_ylabel("Avg. magnitude")
    a3.set_ylim(ymin=0,ymax=max(AvgMagnitudes)+1)
    a3.set_xlabel("Events")
    #plt.subplot(414)
    #plt.bar(Nos,A)
    #plt.ylabel("log(Max. stroke rate)")

    Fig2, (b1, b2, b3) = plt.subplots(3, 1, sharex = True)
    b1.bar(Nos[int(len(Nos)/2):],X[int(len(Nos)/2):], color=PColour)
    b1.set_ylabel("Max Plume Height/km")
    b1.set_ylim(ymin=ymin1,ymax=ymax1)
    b1.set_title("Shiveluch Plumes and Lightning (2/2)")
    b2.bar(Nos[int(len(Nos)/2):],Y[int(len(Nos)/2):], color=LColour)
    b2.set_ylabel("Strike count")
    b2.set_ylim(ymin=ymin2,ymax=ymax2)
    b3.bar(Nos[int(len(Nos)/2):],Z[int(len(Nos)/2):], color=LColour)
    b3.set_ylabel("Avg. magnitude")
    b3.set_ylim(ymin=0,ymax=(max(AvgMagnitudes)+1))
    b3.set_xlabel("Events")

if DateBarsPlot:
    Day = Dates[0]
    n = 0
    PrevN = 0
    MaxHeight = max(PlumeHeights)
    MaxStrikes = max(StrikeCounts)
    MaxMag = max(AvgMagnitudes)
    for i in range(0, len(DateBarLimits)-1):
        #---Fix labels with actual dates---
        Days = JulianDay(DateBarLimits[i+1]) - JulianDay(DateBarLimits[i])
        LabelPoints = [JulianDay(DateBarLimits[i]) + (Days/(XTicks-1))*j for j in range(0, XTicks)]
        StrLabels = []
        if Days < 1:
            for Point in LabelPoints:
                C.execute("SELECT time(?)", (Point,))
                StrLabels.append(C.fetchall()[0][0])
        else:
            for Point in LabelPoints:
                C.execute("SELECT datetime(?)", (Point,))
                StrLabels.append(C.fetchall()[0][0][:10])
        #-------
        CurrentDateList = []
        while (Day < JulianDay(DateBarLimits[i+1])) and (n < len(Dates)-1):
            CurrentDateList.append(Day)
            n += 1
            Day = Dates[n]
        Fig3, (c1, c2, c3) = plt.subplots(3, 1, sharex = True)
        if CurrentDateList[0] < LabelPoints[0]:
            print("Aaaaaaaaa")
        if CurrentDateList[-1] > LabelPoints[-1]:
            print("noooooooooooo")
        bars = c1.bar(CurrentDateList, PlumeHeights[PrevN:n], color=PColour)
        for j in range(PrevN, n):
            bars[j-PrevN].set_alpha(Alphas[j])
        c1.set_ylabel("Max Plume Height/km")
        c1.set_xlim(LabelPoints[0],LabelPoints[-1])
        c1.set_xticks(LabelPoints)
        c1.set_xticklabels(StrLabels)
        c1.set_ylim(ymax=MaxHeight+1)
        c1.set_title("Shiveluch - plumes by date " + str(i+1) + "/" + str(len(DateBarLimits)-1))
        c2.bar(CurrentDateList,StrikeCounts[PrevN:n], color=LColour)
        c2.set_ylabel("Strike count")
        c2.set_ylim(ymax=MaxStrikes+1)
        c3.bar(CurrentDateList,AvgMagnitudes[PrevN:n], color=LColour)
        c3.set_ylabel("Avg. magnitude")
        c3.set_ylim(ymax=MaxMag+1)
        plt.show()
        PrevN = n

if DOrderedBars:
    plt.figure()
    plt.subplot(411)
    plt.bar(Nos,PlumeHeights)
    plt.ylabel("Max Plume Height/km")
    plt.subplot(412)
    plt.bar(Nos,StrikeCounts)
    plt.ylabel("Strike count")
    plt.subplot(413)
    plt.bar(Nos,AvgMagnitudes)
    plt.ylabel("Avg. magnitude")
    plt.subplot(414)
    plt.bar(Nos,StrokeRates)
    plt.ylabel("log(Max. stroke rate)")
    plt.show()

Conn.commit()
