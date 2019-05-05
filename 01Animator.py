#----------Volcanic Lightning Project----------
#Generic animation script
#Animiate lightning strikes within some time window

#--Parameters--
StartDate = '2014-01-01 00:00:00.000'
EndDate = '2018-02-01 00:00:00.000'

Location = [55.972,160.595]
#[Lat,Lon] - Position to place volcano marker

LatRange = [54.63,57.32] #Max and min latitudes on plot
LonRange = [158.18,162.96] #Max and min longitudes on plot

Title = "Bezymianny, 2014 - 2018"

Frames = 2000
#No. of frames to animate. Higher allows shorter time windows
Hold = 10
#No. of frames to keep displaying strikes after they occur

ActivityStart = "2016-12-15 00:00:00.000"
#Change central location marker at this time

ScaleSize = 50 #km; length of scale bars

MarkerPoints = [[56.653,161.36],[55.972,160.595],[56.056,160.642],[55.832,160.326],[55.131,160.32],[54.049,159.443]]
#Plot additional triangular markers at these points. Useful if looking for
#potential activity at multiple volcanoes

OutputFileName = "AnimationS.htm"
FrameRate = 30  #Frames per second (fps) for animation playback

#--------------
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import math

Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

def JulianDay(Date):
    """Conversion to SQLite juliandays"""
    C.execute("SELECT julianday(?)", (Date,))
    return C.fetchall()[0][0]

def DirectionDistance(Distance, Bearing, Lat,Lon):
    """Finds the new point reached by travelling Distance along Bearing from [Lat, Lon].
    Also uses haversine formula (assuming spherical Earth).
    See: https://www.movable-type.co.uk/scripts/latlong.html for example."""
    Lat = math.radians(Lat)
    Lon = math.radians(Lon)
    s = Distance / 6371 #6371 = Mean Earth Radius / km
    NewLat = math.asin(math.sin(Lat)*math.cos(s) + math.cos(Lat)*math.sin(s)*math.cos(Bearing))
    NewLon = Lon + math.atan2(math.sin(Bearing)*math.sin(s)*math.cos(Lat),math.cos(s)-math.sin(Lat)*math.sin(NewLat))
    return [math.degrees(NewLat),math.degrees(NewLon)]
    
Start = JulianDay(StartDate)
End = JulianDay(EndDate)
StepTime = (End-Start)/Frames
AS = JulianDay(ActivityStart)

ScaleCorner = [LatRange[0] + 0.1, LonRange[0] + 0.1]
VertScale = DirectionDistance(ScaleSize,0,ScaleCorner[0],ScaleCorner[1])
HorScale = DirectionDistance(ScaleSize,math.pi / 2,ScaleCorner[0],ScaleCorner[1])

#--Reduce to dates of interest--
#Reducing to a smaller database improves performance when not using
#the entire range of dates covered
try:
    C.execute("DROP TABLE Reduced")
except:
    pass
C.execute("""CREATE TABLE Reduced
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)""")
C.execute("""INSERT INTO Reduced
SELECT No, Date, Lat, Lon, Mag FROM Strikes
WHERE julianday(Date) BETWEEN ? AND ?""", (Start,End))

C.execute("SELECT * FROM Reduced")

#--Make the animation--
StepLength = (Start-End)/Frames

Fig = plt.figure()
Ax = plt.axes(ylim=LatRange, xlim=LonRange)
for Point in MarkerPoints:
    Ax.scatter(Point[1],Point[0], marker='^',s=10,c="black")
Ax.scatter(Location[1],Location[0], marker='^',s=10,c="yellow") #Volcano location indicator

Points = [Ax.scatter([],[],s=1)]
TimeText = [plt.text(LonRange[1]-math.copysign(1,LonRange[1]),LatRange[0]+math.copysign(0.25,LatRange[0]),StartDate)]
Features = Points + TimeText
Ax.plot([ScaleCorner[1],VertScale[1]],[ScaleCorner[0],VertScale[0]],c="black")
Ax.plot([ScaleCorner[1],HorScale[1]],[ScaleCorner[0],HorScale[0]],c="black")
Ax.text(ScaleCorner[1]+0.1,ScaleCorner[0]+0.1,str(ScaleSize)+"km")

plt.xlabel('Lon')
plt.ylabel('Lat')
plt.title(Title)

def init():
    """Initialize animation."""
    Points[0].set_offsets([])
    TimeText[0].set_text('')
    return Features

def animate(i):
    """Updates with set of points pertaining to step i."""
    TimeBase = Start + i * StepTime
    C.execute("SELECT Lat FROM Reduced WHERE julianday(Date) BETWEEN ? AND ?", (TimeBase, TimeBase+Hold*StepTime))
    Lat = C.fetchall()
    C.execute("SELECT Lon FROM Reduced WHERE julianday(Date) BETWEEN ? AND ?", (TimeBase, TimeBase+Hold*StepTime))
    Lon = C.fetchall()
    Lat.append((0,))
    Lon.append((0,))
    StrikePositions = []
    for j in range(0, len(Lat)):
        StrikePositions.append([Lon[j][0],Lat[j][0]])
    PointsArray = np.array(StrikePositions)
    Points[0].set_offsets(PointsArray)
    C.execute("SELECT datetime(?)",(TimeBase + Hold * StepTime,))
    Time = C.fetchall()[0][0]
    TimeText[0].set_text(Time)
    if JulianDay(Time) > AS:
        Ax.scatter(Location[1],Location[0], marker='^',s=10,c="red")
    return Features

Anim = animation.FuncAnimation(Fig, animate, init_func=init, frames=Frames, interval=20, blit=True)

Anim.save(OutputFileName, fps=FrameRate, extra_args=['-vcodec', 'libx264'])
