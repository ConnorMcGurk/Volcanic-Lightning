#----------Volcanic Lightning Project----------
#Plume heights and strike rate

#Output:
#Figure 1: Rate plotted against plume height (excluding zeros)
#Figure 2: Rate plotted against plume height (including zeros)
#Figure 3: Rate plotted against plume height (zeros coloured differently)
#Printed values:
#   Plume height - maximum stroke rate correlation (excluding zeros)
#   Number of plumes counted

#---Parameters---

#Coordinates of volcano [Lat,Lon]
Location = [53.9327,168.0377]

ShowTitle = False
Title = "Bogoslof - Lightning Rate and Plume Height"

#File to source plume height record from:
InputFile = "PlumeStrikeAssociation.csv"

StepForward = 1 #Minutes - amount to move the one-hour window for max stroke rate by

StrikeAlpha = 1
NoStrikeAlpha = 0.5 #Used to show plumes without lightning as slightly transparent
StrikeColour = "red"
NoStrikeColour = "orange"
NoPlumeColour = "yellow"

ShowEquation = False    #Whether to label regression line with its equation
DP = 1
#Decimal places to round to in displayed regression line equation
FontSize = 14
#----------------

import matplotlib.pyplot as plt
import sqlite3, csv, numpy, math, statistics

Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

Hour = 1 / 1440     #Time step as a fraction of a day.
#Note: Setting to 1/1440 = 1 minute time step.
JStep = StepForward / (1440*60)

PlumeHeights = []
MaxRates = []
AvgMags = []

AllHeights = []
AllRates = []

ZHeights = []
ZRates = []

NPHeights = []
NPRates = []

with open(InputFile, newline='') as F:
    FReader = csv.reader(F)
    for Line in FReader:
        if Line:    #This statement to catch for blank lines
            Date = Line[0]
            FirstRef = int(Line[3])
            LastRef = int(Line[4])
            Height = float(Line[2])
            if FirstRef and Height:
                C.execute("SELECT julianday(Date) FROM Eruptive2 WHERE No = ?",(FirstRef,))
                FirstDate = C.fetchall()[0][0]
                LastDate = FirstDate + Hour
                C.execute("SELECT No FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                Out = C.fetchall()
                MaxRate = len(Out)
                C.execute("SELECT Mag FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                Mags = C.fetchall()
                if Out[-1][0] < LastRef:
                    KeepGoing = True
                else:
                    KeepGoing = False
                while KeepGoing:
                    FirstDate += JStep
                    LastDate += JStep
                    C.execute("SELECT No FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                    Out = C.fetchall()
                    C.execute("SELECT Mag FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                    Mags = Mags + C.fetchall()
                    if len(Out):
                        #This clause necessary because some activity includes pauses longer than 1hr
                        #Hence, an empty list may be returned without reaching LastRef
                        if Out[-1][0] == LastRef:
                            KeepGoing = False
                    if len(Out) > MaxRate:
                        MaxRate = len(Out)
                PlumeHeights.append(Height)
                MaxRates.append(MaxRate)
                AllHeights.append(Height)
                AllRates.append(MaxRate)
                AvgMags.append(statistics.mean([Mags[i][0] for i in range(0,len(Mags))]))
            elif Height:
                AllHeights.append(Height)
                AllRates.append(0)
                ZHeights.append(Height)
                ZRates.append(0)
            elif FirstRef:       
                C.execute("SELECT julianday(Date) FROM Eruptive2 WHERE No = ?",(FirstRef,))
                FirstDate = C.fetchall()[0][0]
                LastDate = FirstDate + Hour
                C.execute("SELECT No FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                Out = C.fetchall()
                MaxRate = len(Out)
                if Out[-1][0] < LastRef:
                    KeepGoing = True
                else:
                    KeepGoing = False
                while KeepGoing:
                    FirstDate += JStep
                    LastDate += JStep
                    C.execute("SELECT No FROM Eruptive2 WHERE julianday(Date) BETWEEN ? AND ?",(FirstDate, LastDate))
                    Out = C.fetchall()
                    if len(Out):
                        #This clause necessary because some activity includes pauses longer than 1hr
                        #Hence, an empty list may be returned without reaching LastRef
                        if Out[-1][0] == LastRef:
                            KeepGoing = False
                    if len(Out) > MaxRate:
                        MaxRate = len(Out)
                AllRates.append(MaxRate)
                AllHeights.append(0)
                NPRates.append(MaxRate)
                NPHeights.append(0)
                C.execute("SELECT datetime(?)",(FirstDate,))
            else:
                AllHeights.append(0)
                AllRates.append(0)

#print("Average magnitude - stroke rate correlation:")
#print(numpy.corrcoef(AvgMags, MaxRates))
#print(len(AvgMags))
#plt.scatter(AvgMags, MaxRates)
#plt.xlabel("Average Magnitude", fontsize=FontSize)
#plt.ylabel("Max Rate", fontsize=FontSize)
plt.figure()

plt.scatter(MaxRates, PlumeHeights, c=StrikeColour)
plt.xlabel("Max stroke rate (strokes / min)", fontsize=FontSize)
plt.ylabel("Max plume height (km)", fontsize=FontSize)
if ShowTitle:
    plt.title(Title)
plt.xlim(left=0)
print("Plume height - maximum stroke rate correlation (excluding zeros):")
print(numpy.corrcoef(MaxRates,PlumeHeights))
print("Number of plumes counted:")
print(len(MaxRates))
#print(numpy.polyfit(MaxRates,PlumeHeights,1))
[Gradient, Intercept] = numpy.polyfit(MaxRates,PlumeHeights,1)
LineLabel = "y = " + str(round(Intercept,DP)) + " + " + str(round(Gradient,DP)) + "x"
sxPoints = [min(MaxRates), max(MaxRates)]
syPoints = [sxPoints[i] * Gradient + Intercept for i in range(0, len(sxPoints))]
plt.plot(sxPoints, syPoints, c=StrikeColour)

#print(numpy.corrcoef(AllRates,AllHeights))
#print(len(AllRates))
#print(len(AllHeights))
#print(numpy.polyfit(AllRates,AllHeights,1))
#print(AllRates)
#print(AllHeights)
plt.figure()
plt.scatter(AllRates, AllHeights)
plt.xlabel("Max stroke rate (strokes / min)", fontsize=FontSize)
plt.ylabel("Max plume height (km)", fontsize=FontSize)
[Gradient, Intercept] = numpy.polyfit(AllRates,AllHeights,1)
axPoints = [0, max(AllRates)]
ayPoints = [axPoints[i] * Gradient + Intercept for i in range(0, len(axPoints))]
plt.plot(axPoints, ayPoints)
plt.tick_params(labelsize=FontSize)

plt.figure()
plt.scatter(MaxRates, PlumeHeights, alpha=StrikeAlpha, c=StrikeColour)
plt.scatter(ZRates, ZHeights, alpha=NoStrikeAlpha, c=NoStrikeColour)
#plt.scatter(NPRates, NPHeights, alpha=NoStrikeAlpha, c=NoPlumeColour)

plt.plot(sxPoints, syPoints, color=StrikeColour, label=LineLabel)
#plt.plot(axPoints, ayPoints, color=NoStrikeColour)
plt.xlim(left=0)
if ShowEquation:
    plt.legend()
if ShowTitle:
    plt.title(Title)
plt.xlabel("Max stroke rate (strokes / min)", fontsize=FontSize)
plt.ylabel("Max plume height (km)", fontsize=FontSize)
plt.tick_params(labelsize=FontSize)
plt.show()
