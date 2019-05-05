#----------Volcanic Lightning Project----------
#Stroke map colour-coded by polarity and scaled by magnitude

#Output:
#Figure 1 Plot of strokes, colour coded by polarity and scaled by magnitude.
#Optionally overlays wind directions during eruption.

#--Parameters--
StartDate = '2017-05-28 00:00:00.000'
EndDate = '2017-05-29 00:00:00.000'

Location = [53.9327,168.0377]
#[Lat,Lon] - Position to place volcano marker

LatRange = [53.6,54.3] #Max and min latitudes on plot
LonRange = [168.5,167.5] #Max and min longitudes on plot
#Above is full view. Edit these to overide:
LatRange = [53.8,54.2]
LonRange = [168.3,167.7]
AutoRange = False    #If true, overrides the above

ShowTitle = False
Title = "Bogoslof, " + StartDate[:10]

ScaleSize = 10 #km; length of scale bars

ScalePoints = True  #Points showing size scale for spots

ColourBarTicks = 5

VMarkerSize = 20

ScaleByMagnitude = True
PointSize = 1 #If not scaling by magnitude

BarInset = 0.02

#Colour settings for plot - may help with contrast
FaceColour = "black"
MarkerColour = "white"
VMarkerColour = "white"
PosColour = "red"
NegColour = "blue"
PointAlpha = 1
#FaceColour = "white"
#MarkerColour = "black"

ShowWinds = True
#Hysplit wind directions
#Coordinates of point 1hr after start

#May 28th
TenK = [54.162,167.690]
FiveK = [54.165,168.293]
OneK = [54.044,168.239]

#March 8th
#TenK = [53.965,167.192]
#FiveK = [53.967,167.815]
#OneK = [53.936,168.154]

#May 17th
#TenK = [53.654,168.362]
#FiveK = [53.362,168.499]
#OneK = [53.872,168.083]

#Arrow Colour Codes
TColour = (0,1,0)
FColour = (1,1,0)
OColour = (0,1,1)

TKLabel = "10000m"
FKLabel = "5000m"
OKLabel = "1000m"

FontSize = 12
#--------------

import matplotlib.pyplot as plt
import numpy as np
import sqlite3, matplotlib.colors, math
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(Date):
    """Conversion to SQLite juliandays"""
    C.execute("SELECT julianday(?)", (Date,))
    return C.fetchall()[0][0]

def DirectionDistance(Distance, Bearing, Lat,Lon):
    """Finds the new point reached by travelling Distance along Bearing from [Lat, Lon].
    Also uses haversine formula (assuming spherical Earth.
    See: https://www.movable-type.co.uk/scripts/latlong.html"""
    Lat = math.radians(Lat)
    Lon = math.radians(Lon)
    s = Distance / 6371 #6371 = Mean Earth Radius / km
    NewLat = math.asin(math.sin(Lat)*math.cos(s) + math.cos(Lat)*math.sin(s)*math.cos(Bearing))
    NewLon = Lon + math.atan2(math.sin(Bearing)*math.sin(s)*math.cos(Lat),math.cos(s)-math.sin(Lat)*math.sin(NewLat))
    return [math.degrees(NewLat),math.degrees(NewLon)]

#--Reduce to dates of interest--
try:
    C.execute("DROP TABLE Reduced")
except:
    pass
C.execute("""CREATE TABLE Reduced
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
C.execute("""INSERT INTO Reduced
SELECT * FROM Strikes
WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))

C.execute("SELECT Lat FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Lat = C.fetchall()
C.execute("SELECT Lon FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Lon = C.fetchall()
C.execute("SELECT julianday(Date) FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Dates = C.fetchall()
C.execute("SELECT Mag FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Mags = C.fetchall()

if AutoRange:
    LatRange[0] = round(min([Lat[i][0] for i in range(0, len(Lat))]),1) - 0.1
    LatRange[1] = round(max([Lat[i][0] for i in range(0, len(Lat))]),1) + 0.1
    LonRange[1] = round(min([Lon[i][0] for i in range(0, len(Lon))]),1) - 0.1
    LonRange[0] = round(max([Lon[i][0] for i in range(0, len(Lon))]),1) + 0.1

#Setup figure
Fig = plt.figure()
Ax = plt.axes(ylim=LatRange, xlim=LonRange)
ScaleCorner = [LatRange[0] + BarInset, LonRange[0] - BarInset]
VertScale = DirectionDistance(ScaleSize,0,ScaleCorner[0],ScaleCorner[1])
HorScale = DirectionDistance(ScaleSize,3*math.pi / 2,ScaleCorner[0],ScaleCorner[1])
Ax.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c=MarkerColour)
Ax.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c=MarkerColour)
Ax.text(ScaleCorner[1]-BarInset,ScaleCorner[0]+BarInset,str(ScaleSize)+"km",color=MarkerColour, fontsize=FontSize)
Ax.set_facecolor(FaceColour)

for i in range(0, len(Lat)):
    if Mags[i][0] > 0:
        if ScaleByMagnitude:
            Ax.scatter(Lon[i][0],Lat[i][0],c=PosColour,s=Mags[i][0], alpha=PointAlpha)
        else:
            Ax.scatter(Lon[i][0],Lat[i][0],c=NegColour,s=PointSize, alpha=PointAlpha)
    else:
        if ScaleByMagnitude:
            Ax.scatter(Lon[i][0],Lat[i][0],c=NegColour,s=abs(Mags[i][0]), alpha=PointAlpha)
        else:
            Ax.scatter(Lon[i][0],Lat[i][0],c=NegColour,s=PointSize, alpha=PointAlpha)

Ax.scatter(Location[1],Location[0], marker='^',s=VMarkerSize,c=VMarkerColour)
Ax.set_xlabel("Lon", fontsize=FontSize)
Ax.set_ylabel("Lat", fontsize=FontSize)
Ax.tick_params(labelsize=FontSize)

if ShowTitle:
    plt.title(Title)
if ShowWinds:
    ar1 = plt.arrow(Location[1],Location[0],TenK[1]-Location[1],TenK[0]-Location[0],color=TColour,length_includes_head=True)
    ar2 = plt.arrow(Location[1],Location[0],FiveK[1]-Location[1],FiveK[0]-Location[0],color=FColour,length_includes_head=True)
    ar3 = plt.arrow(Location[1],Location[0],OneK[1]-Location[1],OneK[0]-Location[0],color=OColour,length_includes_head=True)
    plt.legend([ar1,ar2,ar3],[TKLabel,FKLabel,OKLabel])
if ScalePoints:
    Ax.scatter(ScaleCorner[1], LatRange[1] - (LatRange[1]-LatRange[0])/20, s=100, color=PosColour)
    Ax.scatter(ScaleCorner[1], LatRange[1] - (LatRange[1]-LatRange[0])/10, s=10, color=PosColour)
    Ax.scatter(ScaleCorner[1], LatRange[1] - 3*(LatRange[1]-LatRange[0])/20, s=10, color=NegColour)
    Ax.scatter(ScaleCorner[1], LatRange[1] - (LatRange[1]-LatRange[0])/5, s=100, color=NegColour)
    Ax.text(ScaleCorner[1]-0.01, (LatRange[1] - (LatRange[1]-LatRange[0])/20)-0.005, " 100kA",fontsize=FontSize,color=MarkerColour)
    Ax.text(ScaleCorner[1]-0.01, LatRange[1] - (LatRange[1]-LatRange[0])/10-0.005, " 10kA",fontsize=FontSize,color=MarkerColour)
    Ax.text(ScaleCorner[1]-0.01, LatRange[1] - 3*(LatRange[1]-LatRange[0])/20-0.005, "-10kA",fontsize=FontSize,color=MarkerColour)
    Ax.text(ScaleCorner[1]-0.01, LatRange[1] - (LatRange[1]-LatRange[0])/5-0.005, "-100kA",fontsize=FontSize,color=MarkerColour)
plt.show()
