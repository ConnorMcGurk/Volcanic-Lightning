#Volcanic Lightning Project
#Plots individual strokes by their time and peak current

#Output:
#Figure 1 Strokes plotted by their time and peak current

#---Parameters---
StartDate = '2014-01-01 00:00:00.000'
EndDate = '2014-07-01 00:00:00.000'
UseJStart = True    #If True, overrides the above
JStart = 2456700.5
JEnd = 2456750.5

VolcColour = "red"
MetColour = "blue"

XTicks = 6
PointSize = 1

ShowTitle = False
Title = "Kelud - Strike Currents by Date"

FontSize = 20

#----------------------------------------
import matplotlib.pyplot as plt
import sqlite3
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

Months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
    }

if UseJStart:
    C.execute("SELECT datetime(?)",(JStart,))
    StartDate = C.fetchall()[0][0]
    C.execute("SELECT datetime(?)",(JEnd,))
    EndDate = C.fetchall()[0][0]

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

C.execute("SELECT julianday(Date) FROM Unlinked WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
MetDates = C.fetchall()
C.execute("SELECT Mag FROM Unlinked WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
MetMags = C.fetchall()

C.execute("SELECT julianday(Date) FROM Eruptive WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
VolcDates = C.fetchall()
C.execute("SELECT Mag FROM Eruptive WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
VolcMags = C.fetchall()

if UseJStart:
    Ax = plt.axes(xlim=(JStart,JEnd))
else:
    Ax = plt.axes(xlim=(JulianDay(StartDate),JulianDay(EndDate)))
Ax.scatter([Date[0] for Date in MetDates],[Mag[0] for Mag in MetMags], c=MetColour, s=PointSize)
Ax.scatter([Date[0] for Date in VolcDates],[Mag[0] for Mag in VolcMags], c=VolcColour, s=PointSize)

#---Fix labels with actual dates---
Start = JulianDay(StartDate)
Days = JulianDay(EndDate)-Start
LabelPoints = [Start + (Days/(XTicks-1))*i for i in range(0, XTicks)]
StrLabels = []
if Days < 1:
    for Point in LabelPoints:
        C.execute("SELECT time(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    Ax.set_xlabel("Time", fontsize=FontSize)
else:
    for Point in LabelPoints:
        C.execute("SELECT datetime(?)", (Point,))
        LabDate = C.fetchall()[0][0]
        assert int(LabDate[11:13]) == 0
        Month = Months.get(int(LabDate[5:7]))
        StrLabels.append(LabDate[8:11] + Month)
    Ax.set_xlabel("Date", fontsize=FontSize)
Ax.set_xticks(LabelPoints)
Ax.set_xticklabels(StrLabels)
Ax.tick_params(labelsize=FontSize)
Ax.set_ylabel("Peak Current", fontsize=FontSize)
if ShowTitle:
    plt.title(Title)

plt.show()
