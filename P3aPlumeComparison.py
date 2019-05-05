#----------Volcanic Lightning Project----------
#Plume heights and stroke records
#Can also be used to populate tables of volcanic / meteorological strokes

#Output:
#*Figure 1 Plume height, stroke count, mean magnitude and max rate ordered by height
#Figure 2 Plume height, stroke count and mean magnitude plotted by date
#*Figure 3 Plume height, stroke count, mean magnitude and max rate ordered by date
#Figure 4 Scatter plot of stroke count against recorded plume height
#Those marked with * can be disabled in the options below
#Printed values:
#   Plume Height - Stroke Count Correlation - Excluding zero values
#   Number of Plumes Counted in correlation
#   Magnitude - Stroke Count Correlation
#   Magnitude - Plume Height Correlation

#---Parameters---
Title = "Bogoslof - Plume Records"

#Coordinates of volcano [Lat,Lon]
Location = [53.9327,168.0377]

ShowTitle = False
Title = "Plume Heights, Stroke Counts and Average Magnitudes"

#File to source plume height record from:
InputFile = "PlumeStrikeAssociation.csv"

RateNumber = 50

XTicks = 5
ManualXTicks = True #If true, overrides the above with the values below
LabelDates = ["2017-01-01", "2017-03-01", "2017-05-01","2017-07-01","2017-09-01"]
StrLabels = ["Jan 2017","Mar","May","Jul","Sept"]   #Text labels
ManualXLim = True
XLimDate = "2017-09-01" #End point if manually setting y limit

HeightOrderedBars = True    #Whether to show a plot of properties ordered by plume height
DateOrderedBars = True  #Whether to show a plot of properties ordered by date, without gaps

#Chart display settings:
HeightColour = "black"
StrikeColour = "red"
FontSize = 20
BarWidth = 0.7
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
TotalStrikes = []
NZPlumes = []


#This section is used to populate separate Volcanic and Meteorological lightning tables
#Keep commented out if running the code with these tables already populated
#C.execute("""CREATE TABLE Eruptive2
#(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
#C.execute("""CREATE TABLE Met2
#(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
#C.execute("""INSERT INTO Met2
#SELECT No, Date, Lat, Lon, Mag FROM Strikes""")
#All strokes are inserted into the Meteorological table initially; volcanic lightning strokes will be
#removed from this later

with open(InputFile, newline='') as F:
    FReader = csv.reader(F)
    for Line in FReader:
        if Line:
            Date = Line[0]
            FirstRef = Line[3]
            LastRef = Line[4]
            Height = float(Line[2])
            if FirstRef:
                C.execute("SELECT No, Date, Lat, Lon, Mag FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                Out = C.fetchall()
                #These two lines to populate Volcanic and Meteorological tables
                #Keep commented out if these are already populated
                #C.execute("INSERT INTO Eruptive2 SELECT No, Date, Lat, Lon, Mag FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                #C.execute("DELETE FROM Met2 WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                #---
                C.execute("SELECT julianday(Date) FROM Strikes WHERE No BETWEEN ? AND ?",(FirstRef, LastRef))
                OutDates = C.fetchall()
            else:
                Out = []
            StrikeCount = len(Out)
            PeakCurrents = []
            Magnitudes = []
            for i in range(0, StrikeCount):
                PeakCurrents.append(Out[i][4])
                Magnitudes.append(abs(Out[i][4]))
            PlumeHeights.append(Height)
            Dates.append(JulianDay(Date))
            if StrikeCount:
                StrikeCounts.append(math.log10(StrikeCount))
                AvgMagnitudes.append(numpy.mean(Magnitudes))
            else:
                StrikeCounts.append(0)
                AvgMagnitudes.append(0)
            if Height:
                    TotalStrikes.append(StrikeCount)
                    NZPlumes.append(Height)
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

AllRates = [0, 6, 5, 0, 29, 7, 0, 9, 0, 0, 10, 0, 0, 41, 13, 33, 0, 0, 1, 0, 4, 1, 9, 14, 11, 1, 15, 0, 0, 0, 11, 0, 34, 6, 47, 0, 0, 0, 0, 77, 69, 0, 0, 0, 5, 1, 0, 4, 0, 2, 0, 0, 1, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
AllHeights = [0, 0, 0, 10.3, 10.7, 9.1, 0, 9.1, 0, 6.1, 0, 0, 0, 10.0, 10.7, 10.7, 5.5, 4.4, 0, 4.6, 9.4, 11.0, 9.1, 10.7, 9.8, 7.6, 7.6, 0, 7.6, 0, 11.6, 7.6, 7.6, 7.6, 10.7, 0, 0, 0, 5.5, 10.4, 13.7, 7.3, 0, 1.8, 10.4, 7.6, 0, 11.0, 7.6, 9.1, 0, 11.0, 8.5, 9.8, 9.1, 6.1, 0, 9.7, 0, 0, 0, 0, 0, 0, 7.3, 7.9, 0, 9.0, 6.0]
#Direct input here retrieved from rate testing script

#print("Plume Height - Stroke Count Correlation:")
#print(numpy.corrcoef(PlumeHeights, StrikeCounts))
#print("Number of Plumes Counted:")
#print(len(PlumeHeights))
#plt.scatter(PlumeHeights, StrikeCounts)
#plt.show()

#print("Average Magnitude - Stroke Count Correlation:")
#print(numpy.corrcoef(AvgMagnitudes, StrikeCounts))
#plt.scatter(AvgMagnitudes, StrikeCounts)
#print("Average Magnitude - Plume Height Correlation:")
#print(numpy.corrcoef(AvgMagnitudes, PlumeHeights))
#plt.show()

m1 = []
p1 = []
c1 = []

for i in range(0, len(StrikeCounts)):
    if StrikeCounts[i] and PlumeHeights[i]:
        c1.append(StrikeCounts[i])
        m1.append(AvgMagnitudes[i])
        p1.append(PlumeHeights[i])

print("Plume Height - Stroke Count Correlation - Excluding zero values:")
print(numpy.corrcoef(c1,p1))
print("Number of Plumes Counted:")
print(len(c1))
[Gradient, Intercept] = numpy.polyfit(c1,p1,1)
#plt.scatter(c1,p1)
axPoints = [0, max(c1)]
ayPoints = [axPoints[i] * Gradient + Intercept for i in range(0, len(axPoints))]
#plt.plot(axPoints, ayPoints)
#plt.figure()

print("Magnitude - Stroke Count Correlation")
print(numpy.corrcoef(m1, c1))
#plt.scatter(m1, c1)
print("Magnitude - Plume Height Correlation")
print(numpy.corrcoef(m1, p1))

#p2 = []
#for i in range(0, len(p1)):
#    d = Intercept + Gradient * c1[i]
#    p2.append(p1[i] - d)
#print(numpy.corrcoef(m1,p2))
#plt.show()

#print(len(PlumeHeights))
#print(len(AllRates))
X = sorted(PlumeHeights, reverse=True)
Y = [x for _,x in sorted(zip(PlumeHeights,StrikeCounts),key=TakeFirst, reverse=True)]
Z = [x for _,x in sorted(zip(PlumeHeights,AvgMagnitudes),key=TakeFirst, reverse=True)]
A = [x for _,x in sorted(zip(PlumeHeights,StrokeRates),key=TakeFirst, reverse=True)]
#A = [x for _,x in sorted(zip(AllHeights,AllRates),key=TakeFirst, reverse=True)]

LogA = []
for i in range(0, len(A)):
    if A[i]:
        LogA.append(math.log10(A[i]))
    else:
        LogA.append(0)

plt.subplot(411)
plt.bar(Nos,X, color=HeightColour)
plt.ylabel("Max Plume Height/km")
if ShowTitle:
    plt.title(Title)
plt.subplot(412)
plt.bar(Nos,Y, color=StrikeColour)
plt.ylabel("log(Strike count)")
plt.subplot(413)
plt.bar(Nos,Z, color=StrikeColour)
plt.ylabel("Avg. magnitude")
plt.subplot(414)
plt.bar(Nos,LogA, color=StrikeColour)
plt.ylabel("log(Max. stroke rate)")
plt.ylabel("log(Max strikes/min)")

#X2 = []
#A2 = []
#for i in range(0, len(A)):
#    if X[i]:#A[i] and 
#        X2.append(X[i])        
#        A2.append(A[i])
#plt.figure()
#plt.scatter(X2, A2)
#plt.ylabel("log(Max. stroke rate / strikes min-1)")
#plt.xlabel("Max. plume height")
#plt.show()

#---Fix labels with actual dates---
if ManualXTicks:
    LabelPoints = [JulianDay(Date) for Date in LabelDates]
else:
    LabelPoints = [Dates[0]]
    Days = Dates[-1] - Dates[0]
    LabelPoints = [Dates[0] + (Days/(XTicks-1))*i for i in range(0, XTicks)]
    StrLabels = []
    if Days < 1:
        for Point in LabelPoints:
            C.execute("SELECT time(?)", (Point,))
            StrLabels.append(C.fetchall()[0][0])
        plt.xlabel("Time")
    else:
        for Point in LabelPoints:
            C.execute("SELECT datetime(?)", (Point,))
            StrLabels.append(C.fetchall()[0][0][:10])
        plt.xlabel("Date")
#A.set_xticks(LabelPoints,StrLabels)
#plt.xticks(LabelPoints,StrLabels)

F, (Ax1,Ax2,Ax3) = plt.subplots(3,1, sharex=True)
Ax1.bar(Dates, PlumeHeights, color=HeightColour, width=BarWidth)
Ax1.set_ylabel("Max Height/km", fontsize=FontSize)
#Ax1.set_xticks(LabelPoints)
Ax1.set_xticklabels([], fontsize=FontSize)
Ax2.bar(Dates,StrikeCounts, color=StrikeColour, width=BarWidth)
Ax2.set_ylabel("log(Stroke count)", fontsize=FontSize)
Ax2.yaxis.tick_right()
Ax2.yaxis.set_label_position("right")
Ax2.set_xticks(LabelPoints)
#Ax2.set_xticks(LabelPoints,StrLabels, fontsize=FontSize)
Ax2.set_xticklabels([], fontsize=FontSize)
Ax3.bar(Dates,AvgMagnitudes, color=StrikeColour, width=BarWidth)
Ax3.set_ylabel("Avg. magnitude / kA", fontsize=FontSize)
plt.xticks(LabelPoints,StrLabels, fontsize=FontSize)
Axes = (Ax1,Ax2,Ax3)
for Ax in Axes:
    Ax.yaxis.set_tick_params(labelsize=FontSize)
    if ManualXLim:
        Ax.set_xlim(left=(Dates[0]-1),right=(JulianDay(XLimDate)))
    else:
        Ax.set_xlim(left=(Dates[0]-1),right=(Dates[-1]+1))
#Ax1.yaxis.set_tick_params(labelsize=FontSize)
#Ax2.yaxis.set_tick_params(labelsize=FontSize)
#Ax3.yaxis.set_tick_params(labelsize=FontSize)
#plt.subplot(414)
#plt.bar(Dates,StrokeRates)
#plt.ylabel("log(Max. stroke rate)")
#plt.show()

if DateOrderedBars:
    plt.figure()
    plt.subplot(411)
    plt.bar(Nos,PlumeHeights)
    plt.ylabel("Max Plume Height/km")
    plt.subplot(412)
    plt.bar(Nos,StrikeCounts)
    plt.ylabel("log(Strike count)")
    plt.subplot(413)
    plt.bar(Nos,AvgMagnitudes)
    plt.ylabel("Avg. magnitude")
    plt.subplot(414)
    plt.bar(Nos,StrokeRates)
    plt.ylabel("log(Max. stroke rate)")

plt.figure()
plt.scatter(StrikeCounts, PlumeHeights)
plt.xlabel("log(Stroke Count)")
plt.ylabel("Plume Height")
#print(numpy.corrcoef(TotalStrikes, PlumeHeights))
#plt.scatter(TotalStrikes, PlumeHeights)
#print(numpy.corrcoef(TotalStrikes, NZPlumes))
#plt.scatter(TotalStrikes, NZPlumes)

plt.show()

#Conn.commit()
#This line to save input into tables. Leave commented out if tables are already populated.
        
