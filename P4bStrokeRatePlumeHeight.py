#----------Volcanic Lightning Project----------
#Plume heights and strike rate
#This script for an input file which has an additional column for repeated
#heights or resuspended plumes, which can optionally be removed from analysis

#Output:
#Figure 1: Rate plotted against plume height (excluding zeros)
#Figure 2: Rate plotted against plume height (including zeros)
#Figure 3: Rate plotted against plume height (zeros coloured differently)
#Printed values:
#   Plume height - maximum stroke rate correlation (excluding zeros)
#   Number of plumes counted


#---Parameters---

#Coordinates of volcano [Lat,Lon]
Location = [56.653,161.36]

ShowTitle = False
Title = "Shiveluch - Lightning Rate and Plume Height"

#File to source plume height record from:
InputFile = "PlumeStrikeAssociation.csv"

StepForward = 1 #Minutes - amount to move the one-hour window for max stroke rate by

RemoveRepetitions = False
RemoveResuspended = True

StrikeAlpha = 1
NoStrikeAlpha = 0.5 #Used to show plumes without lightning as slightly transparent
StrikeColour = "red"
NoStrikeColour = "orange"

ShowEquation = False
DP = 5
#Decimal places to round to in displayed regression line equation

FontSize = 18
#----------------

import matplotlib.pyplot as plt
import sqlite3, csv, numpy, math

Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

Hour = 1 / 1440
JStep = StepForward / (1440*60)

PlumeHeights = []
MaxRates = []

AllHeights = []
AllRates = []

ZHeights = []
ZRates = []

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
                FirstRef = int(Line[4])
                LastRef = int(Line[5])
                Height = float(Line[3])
                if FirstRef and Height:
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
                    PlumeHeights.append(Height)
                    MaxRates.append(MaxRate)
                    AllHeights.append(Height)
                    AllRates.append(MaxRate)
                elif Height:
                    AllHeights.append(Height)
                    AllRates.append(0)
                    ZHeights.append(Height)
                    ZRates.append(0)

plt.scatter(MaxRates, PlumeHeights, c=StrikeColour)
plt.xlabel("Max stroke rate (strokes / min)", fontsize=FontSize)
plt.ylabel("Max plume height (km)", fontsize=FontSize)
plt.title(Title)
plt.xlim(left=0)
plt.tick_params(labelsize=FontSize)
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
#print(numpy.polyfit(AllRates,AllHeights,1))
plt.figure()
plt.scatter(AllRates, AllHeights)
plt.xlabel("Max stroke rate (strokes / min)", fontsize=FontSize)
plt.ylabel("Max plume height (km)", fontsize=FontSize)
[Gradient, Intercept] = numpy.polyfit(AllRates,AllHeights,1)
axPoints = [0, max(AllRates)]
ayPoints = [axPoints[i] * Gradient + Intercept for i in range(0, len(axPoints))]
plt.tick_params(labelsize=FontSize)
plt.plot(axPoints, ayPoints)

plt.figure()
plt.scatter(MaxRates, PlumeHeights, alpha=StrikeAlpha, c=StrikeColour)
plt.scatter(ZRates, ZHeights, alpha=NoStrikeAlpha, c=NoStrikeColour)
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
