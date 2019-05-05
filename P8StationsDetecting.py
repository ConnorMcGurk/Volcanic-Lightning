#----------Volcanic Lightning Project----------
#Strike map coloured by number of stations detecting  a strike
#To check for position biases

#Output:
#Figure 1 Stroke positions, colour coded by the number of stations detecting
#them, above a minimum value below. Done in two frames: Minimum values only
#on left, values greater than this only on right

#--Parameters--
StartDate = '2011-05-21 19:00:00.000'
EndDate = '2011-05-23 15:40:00.000'

Location = [64.416,-17.316]
#[Lat,Lon] - Position to place volcano marker

LatRange = [53.7,54.4] #Max and min latitudes on plot
LonRange = [167.5,168.5] #Max and min longitudes on plot
AutoRange = True   #If true, overrides the above

ShowTitle = False
Title = "Grimsvotn, 21-23rd May 2011"# + StartDate[:10]

ScaleSize = 20 #km; length of scale bars

ColourBarTicks = 5

PointSize = 1
VMarkerSize = 20

BarInset = 0.02

#Colour settings for plot - may help with contrast
FaceColour = "black"
MarkerColour = "white"
VMarkerColour = "white"
#FaceColour = "white"
#MarkerColour = "black"

MinStations = 3

FontSize = 16
DisplayColourBar = False
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
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL, Stations INT)""")
C.execute("""INSERT INTO Reduced
SELECT No, Date, Lat, Lon, Mag, Stations FROM Strikes
WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))

if AutoRange:
    C.execute("SELECT MAX(Lat) FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
    MaxLat = C.fetchall()[0][0]
    C.execute("SELECT MAX(Lon) FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
    MaxLon = C.fetchall()[0][0]
    C.execute("SELECT MIN(Lat) FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
    MinLat = C.fetchall()[0][0]
    C.execute("SELECT MIN(Lon) FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
    MinLon = C.fetchall()[0][0]
    LatRange[0] = round(MinLat,1) - 0.1
    LatRange[1] = round(MaxLat,1) + 0.1
    LonRange[0] = round(MinLon,1) - 0.1
    LonRange[1] = round(MaxLon,1) + 0.1

#Setup figure
Fig, (Ax,Ax2) = plt.subplots(1,2)
#Fig = plt.figure()
#Ax = plt.axes(ylim=LatRange, xlim=LonRange)
Ax.set_ylim(bottom=LatRange[0],top=LatRange[1])
Ax.set_xlim(left=LonRange[0],right=LonRange[1])
Ax2.set_ylim(bottom=LatRange[0],top=LatRange[1])
Ax2.set_xlim(left=LonRange[0],right=LonRange[1])

#Place scale bars
ScaleCorner = [LatRange[0] + BarInset, LonRange[0] + BarInset]
VertScale = DirectionDistance(ScaleSize,0,ScaleCorner[0],ScaleCorner[1])
HorScale = DirectionDistance(ScaleSize,math.pi / 2,ScaleCorner[0],ScaleCorner[1])
Ax.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c=MarkerColour)
Ax.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c=MarkerColour)
Ax.text(ScaleCorner[1]+BarInset,ScaleCorner[0]+BarInset,str(ScaleSize)+"km",color=MarkerColour, fontsize=FontSize)
Ax.set_facecolor(FaceColour)
Ax2.set_facecolor(FaceColour)
Ax2.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c=MarkerColour)
Ax2.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c=MarkerColour)
Ax2.text(ScaleCorner[1]+BarInset,ScaleCorner[0]+BarInset,str(ScaleSize)+"km",color=MarkerColour, fontsize=FontSize)


C.execute("SELECT Lat FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Lat = C.fetchall()
C.execute("SELECT Lon FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Lon = C.fetchall()
C.execute("SELECT Stations FROM Reduced WHERE Date BETWEEN ? AND ?", (StartDate,EndDate))
Stations = C.fetchall()

for i in range(0, len(Stations)):
    Stations[i] = Stations[i][0]

#Colour and colour bar settings
Cmap = plt.cm.rainbow
Norm = matplotlib.colors.Normalize(vmin=min(Stations),vmax=max(Stations))
CBar = plt.cm.ScalarMappable(cmap=Cmap, norm=Norm)
CBar.set_array([])
if DisplayColourBar:
    DispBar = Fig.colorbar(CBar)
    DispBar.set_label("No. Stations detecting", fontsize=FontSize)
    DispBar.ax.tick_params(labelsize=FontSize)

for i in range(0, len(Lat)):
    if Stations[i] == MinStations:
        Ax.scatter(Lon[i][0],Lat[i][0],c=Cmap(Norm(Stations[i])),s=PointSize)
    else:
        Ax2.scatter(Lon[i][0],Lat[i][0],c=Cmap(Norm(Stations[i])),s=PointSize)

Ax.scatter(Location[1],Location[0], marker='^',s=VMarkerSize,c=VMarkerColour)
Ax2.scatter(Location[1],Location[0], marker='^',s=VMarkerSize,c=VMarkerColour)
Ax.set_xlabel("Lon", fontsize=FontSize)
Ax.set_ylabel("Lat", fontsize=FontSize)
Ax2.set_xlabel("Lon", fontsize=FontSize)
Ax2.set_ylabel("Lat", fontsize=FontSize)
Ax.yaxis.set_tick_params(labelsize=FontSize)
Ax.xaxis.set_tick_params(labelsize=FontSize)
Ax2.yaxis.set_tick_params(labelsize=FontSize)
Ax2.xaxis.set_tick_params(labelsize=FontSize)
if ShowTitle:
    plt.title(Title)
plt.show()
