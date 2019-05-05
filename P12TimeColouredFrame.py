#----------Volcanic Lightning Project----------
#Strike map colour-coded by time
#Aim to produce a comparable record to animations in a single figure

#Output:
#   Figure 1: Points plotted between the times defined below and coloured by time.

#--Parameters--
StartDate = "2016-03-17 09:30:00.000"
EndDate = "2016-03-17 11:10:00.000"

Location = [-7.938, 112.304]
#[Lat,Lon] - Position to place volcano marker

#LatRange = [-10,-6] #Max and min latitudes on plot
#LonRange = [110,114] #Max and min longitudes on plot
AutoLatRange = True     #If False, uncomment the above

ShowTitle = False
Title = "Kelud, " + StartDate[:10]

ScaleSize = 50 #km; length of scale bars

AutoCBarTicks = True   #If true, decide on best number of tick markers
ColourBarTicks = 5      #Else, use this many

PointSize = 1
VMarkerSize = 20

BarInset = 0.1

FontSize = 12

#Colour settings for plot - may help with contrast
FaceColour = "black"
MarkerColour = "white"
VMarkerColour = "white"

Reverse = False
#Whether to show earlier strokes on top. These will often be overprinted
#by later ones if this is false, and will overprint later ones if it is true.
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

if AutoLatRange:
    LatRange = [DirectionDistance(150,math.pi, Location[0], Location[1])[0],DirectionDistance(150,0, Location[0], Location[1])[0]]
    LonRange = [DirectionDistance(150,3*math.pi/2, Location[0], Location[1])[1],DirectionDistance(150,math.pi/2, Location[0], Location[1])[1]]

#Setup figure
Fig = plt.figure()
Ax = plt.axes(ylim=LatRange, xlim=LonRange)

#Place scale bars
ScaleCorner = [LatRange[0] + BarInset, LonRange[0] + BarInset]
VertScale = DirectionDistance(ScaleSize,0,ScaleCorner[0],ScaleCorner[1])
HorScale = DirectionDistance(ScaleSize,math.pi / 2,ScaleCorner[0],ScaleCorner[1])
Ax.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c=MarkerColour)
Ax.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c=MarkerColour)
Ax.text(ScaleCorner[1]+BarInset,ScaleCorner[0]+BarInset,str(ScaleSize)+"km",color=MarkerColour, fontsize=FontSize)
Ax.set_facecolor(FaceColour)

#Colour and colour bar settings
Cmap = plt.cm.rainbow
Norm = matplotlib.colors.Normalize(vmin=JulianDay(StartDate),vmax=JulianDay(EndDate))
CBar = plt.cm.ScalarMappable(cmap=Cmap, norm=Norm)
Start = JulianDay(StartDate)
End = JulianDay(EndDate)

if AutoCBarTicks:
    z = (End-Start)*24*60
    for ColourBarTicks in [5,6,4,7,3,8,9,10,2]:
        if z % (ColourBarTicks-1) < 0.001:
            break
        
TickPoints = np.linspace(Start, End, num=ColourBarTicks)
StrLabels = []
if End - Start < 1:
    if AutoCBarTicks:
        for Point in TickPoints:
            C.execute("SELECT time(?)", (Point,))
            LabelTime = C.fetchall()[0][0]
            assert int(LabelTime[6:8]) == 0
            StrLabels.append(LabelTime[:5])
    else:
        for Point in TickPoints:
            C.execute("SELECT time(?)", (Point,))
            StrLabels.append(C.fetchall()[0][0])
    plt.xlabel("Time", fontsize=FontSize)
else:
    for Point in TickPoints:
        C.execute("SELECT datetime(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    plt.xlabel("Date", fontsize=FontSize)
CBar.set_array([])
DispBar = Fig.colorbar(CBar, ticks=TickPoints)
DispBar.set_ticklabels(StrLabels)
DispBar.ax.tick_params(labelsize=FontSize)

if Reverse:
    C.execute("SELECT Lat FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No DESC", (StartDate,EndDate))
    Lat = C.fetchall()
    C.execute("SELECT Lon FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No DESC", (StartDate,EndDate))
    Lon = C.fetchall()
    C.execute("SELECT julianday(Date) FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No DESC", (StartDate,EndDate))
    Dates = C.fetchall()
else:
    C.execute("SELECT Lat FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No ASC", (StartDate,EndDate))
    Lat = C.fetchall()
    C.execute("SELECT Lon FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No ASC", (StartDate,EndDate))
    Lon = C.fetchall()
    C.execute("SELECT julianday(Date) FROM Strikes WHERE Date BETWEEN ? AND ? ORDER BY No ASC", (StartDate,EndDate))
    Dates = C.fetchall()    
for i in range(0, len(Lat)):
    Ax.scatter(Lon[i][0],Lat[i][0],c=Cmap(Norm(Dates[i])),s=PointSize)

Ax.scatter(Location[1],Location[0], marker='^',s=VMarkerSize,c=VMarkerColour)
plt.xlabel("Lon", fontsize=FontSize)
plt.ylabel("Lat", fontsize=FontSize)
Ax.tick_params(labelsize=FontSize)
if ShowTitle:
    plt.title(Title, fontsize=FontSize)
plt.show()
