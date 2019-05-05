#Volcanic Lightning project
#Rate of increase in volcanic and meteorological storms

#Output:
#Figure 1: Histograms of stroke rates in volcanic and meteorological storms
#Printed values:
#   If stroke rate crosses a threshold defined below, the time taken to reach
#   this from a stroke rate of zero, and the date on which this occurs.

#---Parameters---
StartDate = "2013-02-01 00:00:00.000"
EndDate = "2018-02-02 00:00:00.000"

UpperThreshold = 300    #strokes / TimeInterval
#LowerThreshold = 0
TimeInterval = 1 #Minutes

SplitPeriod = 2
#Number of times to select a reduced table, for processing efficiency

MetColour = "blue"
VolcColour = "red"
ShowTitle = False
Title = "Bogoslof - Lightning Rates"

FontSize = 12

#-----------------
import sqlite3, numpy
import matplotlib.pyplot as plt
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

Start = JulianDay(StartDate)
End = JulianDay(EndDate)
SplitDates = numpy.linspace(Start,End, SplitPeriod)

TimeStep = TimeInterval / 1440

Started = False
TimeSince = 0
MetCounts = []
VolcCounts = []

for i in range(0, len(SplitDates)-1):
    StartTime = SplitDates[i]
    EndTime = SplitDates[i+1]
    BinCount = 0
    Counter = 0
    while (StartTime + Counter*TimeStep) < EndTime:
        Counter += 1
    Bins = [StartTime + TimeStep*j for j in range(0,Counter)]
    C.execute("DELETE FROM T")
    C.execute("""INSERT INTO T
    SELECT * FROM Met2 WHERE julianday(Date) BETWEEN ? AND ?""", (StartTime,EndTime))
    C.execute("DELETE FROM Reduced")
    C.execute("""INSERT INTO Reduced
    SELECT * FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?""", (StartTime,EndTime))
    for j in range(0, len(Bins)-1):
        C.execute("""SELECT COUNT(*) FROM T WHERE julianday(Date) BETWEEN ? AND ?""", (Bins[j],Bins[j+1]))
        MetCounts.append(C.fetchall()[0][0])
        C.execute("""SELECT COUNT(*) FROM Reduced WHERE julianday(Date) BETWEEN ? AND ?""", (Bins[j],Bins[j+1]))
        VolcCounts.append(C.fetchall()[0][0])

NZMCounts = []
NZVCounts = []
for k in range(0, len(MetCounts)):
    if Started:
        TimeSince += 1
    if MetCounts[k]:
        NZMCounts.append(MetCounts[k])
        Started = True
        if MetCounts[k] > UpperThreshold:
            print("-------")
            print("Threshold crossed - meteorological")
            print("Rise time from zero strokes/minute:")
            print(TimeSince)
            print("Time threshold crossed:")
            print(StartTime + (TimeStep * k))
            C.execute("SELECT datetime(?)",(StartTime + (TimeStep * k),))
            print("Date threshold crossed")
            print(C.fetchall()[0][0])
            print("-------")
    else:
        Started = False
        TimeSince = 0

for k in range(0, len(VolcCounts)):
    if Started:
        TimeSince += 1
    if VolcCounts[k]:
        NZVCounts.append(VolcCounts[k])
        Started = True
        if VolcCounts[k] > UpperThreshold:
            print("-------")
            print("Threshold crossed - meteorological")
            print("Rise time from zero strokes/minute:")
            print(TimeSince)
            print(StartTime + (TimeStep * k))
            C.execute("SELECT datetime(?)",(StartTime + (TimeStep * k),))
            print(C.fetchall()[0][0])
            print("-------")
    else:
        Started = False
        TimeSince = 0

Fig, (Ax1,Ax2) = plt.subplots(2,1,sharex=True,sharey=True)
Bins = [0.5+i for i in range(0, max(NZVCounts))]
Ax1.hist(NZVCounts,bins=Bins,color=VolcColour, label="Volcanic")
Ax1.legend(fontsize=FontSize)
if ShowTitle:
    Ax1.set_title(Title, fontsize=FontSize)
Ax2.hist(NZMCounts,bins=Bins,color=MetColour,label="Meteorological")
Ax2.legend(fontsize=FontSize)
Ax2.set_xlabel("Strokes / Min", fontsize=FontSize)
Ax1.set_ylabel("Frequency Density", fontsize=FontSize)
Ax2.set_ylabel("Frequency Density", fontsize=FontSize)
Ax2.tick_params(labelsize=FontSize)
Ax1.tick_params(labelsize=FontSize)
Ax1.set_xlim(left=0)
plt.show()
