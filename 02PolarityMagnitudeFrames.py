#----------Volcanic Lightning Project----------
#Animation script, adapted to show polarity (by colour) and magnitude (by size)
#Saves frames. Does not currently compile saved frames into an animation
#View frames individually for analysis of this

#--Parameters--
StartDate = '2011-05-21 19:00:00.000'
EndDate = '2011-05-23 15:40:00.000'

Location = [64.416,-17.316]
#[Lat,Lon] - Position to place volcano marker
MarkerColour = "black"

AutoRange = False    #If true, assign limits at the radius below; else use the ones below
LimitDistance = 150     #km
LatRange = [63.5,65.5] #Max and min latitudes on plot
LonRange = [-19,-15.5] #Max and min longitudes on plot

Title = "Grimsvotn, May 2011"

Frames = 100
#No. of frames to animate. Higher allows shorter time windows

ScaleSize = 50 #km; length of scale bars

MarkerPoints = []   #Place additional triangular markers at any points listed
SecondColour = "black"

PosColour = "red"
NegColour = "blue"

OutputFolder = 'ColourFrames\\'
#Save destination for frames. Be sure to end this with \\.
#--------------
#Adjust for positions of scale bar and time stamp
TStampLInset = 1.5
ScaleUInset = 0.05
ScaleRInset = 0.05
TStampUInset = ScaleUInset

#Figure size settings
Height = 6  #In inches (... :/ )
#Width auto-determined to make distances in each direction approx. equal
#--------------

import sqlite3, math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

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

def Distance(VCoords, SCoords):
    """Calculate the distance in km between two points given in decimal degrees.
    Found this here: https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points/15742266
    Uses Haversine formula, i.e. assuming perfectly spherical earth"""
    #Convert to radians
    lon1,lat1,lon2,lat2 = map(math.radians, VCoords+SCoords)
    #Apply Haversine formula
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    #Earth radius = 6371km
    return 6371 * c

def SetSize(w, h, ax):
    """Sets axes to a fixed size.
    See: https://stackoverflow.com/questions/44970010/axes-class-set-explicitly-size-width-height-of-axes-in-given-units"""
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)

#Determine axes width
YKm = Distance([LatRange[0],Location[1]],[LatRange[1],Location[1]])
XKm = Distance([Location[0],LonRange[0]],[Location[0],LonRange[1]])
#print(XKm)
#print(YKm)
#Width = Height * (YKm / XKm)
    
Start = JulianDay(StartDate)
End = JulianDay(EndDate)
StepTime = (End-Start)/Frames
#AS = JulianDay(ActivityStart)

if AutoRange:
    #Determines axis limits.
    #Note: To change direction of the axes, simply exchange the 0s and 1s on the LHS
    LatRange[1] = DirectionDistance(150,0,Location[0],Location[1])[0]
    LatRange[0] = DirectionDistance(150,math.pi,Location[0],Location[1])[0]
    LonRange[1] = DirectionDistance(150,math.pi/2,Location[0],Location[1])[1]
    LonRange[0] = DirectionDistance(150,3*math.pi/2,Location[0],Location[1])[1]

#Position of scale bars is a result of the below:
ScaleCorner = [LatRange[0] + ScaleUInset, LonRange[0] + ScaleRInset]
VertScale = DirectionDistance(ScaleSize,0,ScaleCorner[0],ScaleCorner[1])
HorScale = DirectionDistance(ScaleSize,math.pi / 2,ScaleCorner[0],ScaleCorner[1])

#--Reduce to dates of interest--
try:
    C.execute("DROP TABLE Reduced")
except:
    pass
C.execute("""CREATE TABLE Reduced
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
C.execute("""INSERT INTO Reduced
SELECT No, Date, Lat, Lon, Mag FROM Strikes
WHERE julianday(Date) BETWEEN ? AND ?""", (Start,End))

#--Make the animation--

#Fig = plt.figure(figsize = ((YKm/XKm)*Height,Height))
Fig = plt.figure(figsize=(Height,Height))
Ax = plt.axes(ylim=LatRange, xlim=LonRange)
for Point in MarkerPoints:
    Ax.scatter(Point[1],Point[0], marker='^',s=10,c="black")
Ax.scatter(Location[1],Location[0], marker='^',s=10,c=MarkerColour) #Volcano location indicator

Points = []

#Position of time string is set here:
TimeText = [plt.text(LonRange[1]+math.copysign(TStampLInset,LonRange[1]),LatRange[0]+math.copysign(TStampUInset,LatRange[0]),StartDate)]

Features = Points + TimeText
Ax.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c="black")
Ax.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c="black")
Ax.text(ScaleCorner[1]+ScaleRInset,ScaleCorner[0]+ScaleUInset,str(ScaleSize)+"km")

plt.xlabel('Lon')
plt.ylabel('Lat')
plt.title(Title)

#SetSize(Width, Height, Ax)

for i in range(0, Frames):
    LoTime = Start + StepTime * i
    HiTime = Start + StepTime * (i+1)
    C.execute("SELECT Lat, Lon, Mag FROM Reduced WHERE julianday(Date) BETWEEN ? AND ?", (LoTime, HiTime))
    Strokes = C.fetchall()
    #print(Strokes)
    for Stroke in Strokes:
        Mag = Stroke[2]
        if Mag > 0:
            Colour = PosColour
        else:
            Colour = NegColour
        Points.append(Ax.scatter(Stroke[1],Stroke[0],s=abs(Mag),c=Colour))
    C.execute("SELECT datetime(?)",(HiTime,))
    TimeText[0].set_text(C.fetchall()[0][0])
    FigName = str(i) + ".png"
    plt.savefig(OutputFolder +FigName)
    for Point in Points:
        Point.remove()
    Points = []

plt.show()
