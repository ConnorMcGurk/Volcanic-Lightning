#----------Volcanic Lightning Project----------
#Time-distance point plotting script

#Output:
#Figure 1 Stroke magnitude, polarity and distance through time.
#Also plots lines ofthe distance of the "centre of mass" of strokes from the
#vent and the average magnitude of strokes.
#Printed values:
#   Correlation between "centre of mass" distance and average magnitude

#---Parameters---
#Dates to work through
#StartDate = "2017-03-08 08:00:00.000"
#EndDate = "2017-03-08 10:40:00.000"

#StartDate = "2017-05-17 06:50:00.000"
#EndDate = "2017-05-17 08:00:00.000"

StartDate = "2017-05-28 22:35:00.000"
EndDate = "2017-05-28 23:15:00.000"

#Coordinates of volcano [Lat,Lon]
VLocation = [53.9327,168.0377]

ScaleByMagnitude = True
#If True, point size depends on magnitude; else use the one given below
PointSize = 1

#Number of points to label on the x axis. Adjust this if labels are cramped or inadequate.
XTicks = 5

ColourByPolarity = True

PointColour = "red"
NegColour = "blue" #If colouring by polarity, use this for negative polarity
LineColour = "black"
BarColour = "red"
MagColour = "orange"

ShowTitle = False
Title = "Bogoslof, " + StartDate[:10]

COMByTime = False
#If True, calculate "Centre of Mass" in equal time windows; else, use a moving average of strikes
COMPoints = 100
#Number of time windows to consider if True above; else number of strikes in moving average

BinByTime = True
#If true, set bins to the time window below; else, use the number of bins defined below that
BinTime = 1 #minutes
Bins = 100 #Number of bins for histogram

AutoXTicks = True

LegendOn = False
#Whether to display legend. May overlap with data points

ScalePoints = True
#Whether to display point scale markers

FontSize = 12
#---------------------------------------
import sqlite3, math, numpy
import matplotlib.pyplot as plt
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()
PosVLoc = [abs(VLocation[0]),abs(VLocation[1])]

def Distance(VCoords, SCoords):
    """Calculate the distance in km between two points given in decimal degrees.
    Uses Haversine formula, i.e. assuming perfectly spherical earth
    See: https://www.movable-type.co.uk/scripts/latlong.html for example"""
    #Convert to radians
    lat1,lon1,lat2,lon2 = map(math.radians, VCoords+SCoords)
    #Apply Haversine formula
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    #Earth radius = 6371km
    return 6371 * c

def DirectionDistance(Distance, Bearing, Lat,Lon):
    """Finds the new point reached by travelling Distance along Bearing from [Lat, Lon].
    Also uses haversine formula (assuming spherical Earth.
    See: https://www.movable-type.co.uk/scripts/latlong.html"""
    Lat = math.radians(Lat)
    Lon = math.radians(Lon)
    s = Distance / 6371 #6371 = Mean Earth Radius / km
    NewLat = math.asin(math.sin(Lat)*math.cos(s) + math.cos(Lat)*math.sin(s)*math.cos(Bearing))
    NewLon = Lon + math.atan2(math.sin(Bearing)*math.sin(s)*math.cos(Lat),math.cos(s)-math.sin(Lat)*math.sin(NewLat))
    return [math.degrees(NewLat),(math.degrees(NewLon)+540)%360-180]

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

def COM(Lats,Lons):
    """Calculates a "centre of mass" for a set of Lat,Lon points"""
    X = [Distance([0,0],[0,Lons[i][0]]) for i in range(0, len(Lons))]
    Y = [Distance([0,0],[Lats[i][0],0]) for i in range(0, len(Lons))]
    #Distance conversion is carried out to avoid distortion.
    Cx = sum(X) / len(X)
    Cy = sum(Y) / len(Y)
    return [DirectionDistance(Cy,0,0,0)[0],DirectionDistance(Cx,math.pi / 2,0,0)[1]]

if AutoXTicks:
    z = (JulianDay(EndDate)-JulianDay(StartDate))*24*60
    for i in [5,6,4,7,3,8,9,10,2]:
        if z % (i-1) < 0.001:
            XTicks = i
            break

try:
    C.execute("DROP TABLE T")
except:
    pass
C.execute('''CREATE TABLE T
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)''')
C.execute("""INSERT INTO T
SELECT * FROM Strikes WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))


#---Plots point series of distance vs.time---
C.execute("SELECT No FROM T LIMIT 1")
FirstRecordID = int(C.fetchall()[0][0])
C.execute("SELECT No FROM T ORDER BY No DESC LIMIT 1")
LastRecordID = int(C.fetchall()[0][0])
Times = []
Distances = []
Magnitudes = []
for i in range(FirstRecordID, LastRecordID+1):
    C.execute("SELECT julianday(Date), Lat, Lon, Mag FROM T WHERE No = ?", (i,))
    Info = C.fetchall()[0]
    Times.append(Info[0])
    Distances.append(Distance(VLocation,[Info[1],Info[2]]))
    Magnitudes.append(Info[3])
Fig1, (A, A2) = plt.subplots(2,1, gridspec_kw={'height_ratios':[2,1]}, sharex=True)
A3 = A.twinx()
#Fig1 = plt.figure()
#A = Fig1.add_subplot(111)
if ShowTitle:
    A.set_title(Title)
if ColourByPolarity:
    if ScaleByMagnitude:
        for i in range(0, len(Distances)):
            if Magnitudes[i] > 0:
                A.scatter(Times[i], Distances[i], s=abs(Magnitudes[i]), c=PointColour)
            elif Magnitudes[i] < 0:
                A.scatter(Times[i], Distances[i], s=abs(Magnitudes[i]), c=NegColour)
            else:
                print("Oh no!")
    else:
        A.scatter(Times, Distances, s=PointSize, c=PointColour)
else:
    if ScaleByMagnitude:
        A.scatter(Times, Distances, s=[abs(M) for M in Magnitudes], c=PointColour)
    else:
        A.scatter(Times, Distances, s=PointSize, c=PointColour)
plt.xlabel("Date")
plt.ylabel("Distance from vent / km")
Start = JulianDay(StartDate)
End = JulianDay(EndDate)
COMds = [] #Centre of Mass Distances
AvgMag = []
TPoints = []
if COMByTime:
    TimeList = numpy.linspace(Start, End, COMPoints)
    for i in range(0, len(TimeList)-1):
        C.execute("SELECT Lat FROM T WHERE julianday(Date) BETWEEN ? AND ?",(TimeList[i],TimeList[i+1]))
        NLats = C.fetchall()
        C.execute("SELECT Lon FROM T WHERE julianday(Date) BETWEEN ? AND ?",(TimeList[i],TimeList[i+1]))
        NLons = C.fetchall()
        C.execute("SELECT Mag FROM T WHERE julianday(Date) BETWEEN ? AND ?",(TimeList[i],TimeList[i+1]))
        NMags = C.fetchall()
        if len(NLats):
            COMds.append(Distance(PosVLoc,COM(NLats,NLons)))
            AvgMag.append(numpy.mean([abs(NMags[i][0]) for i in range(0, len(NMags))]))
        else:
            COMds.append(0)
            AvgMag.append(0)
        TPoints.append((TimeList[i] + TimeList[i+1]) / 2)
else:
    C.execute("""SELECT Lat FROM T""")
    Lats = C.fetchall()
    C.execute("""SELECT Lon FROM T""")
    Lons = C.fetchall()
    C.execute("""SELECT Mag FROM T""")
    Mags = C.fetchall()
    for i in range(0, len(Lats)-COMPoints):
        COMds.append(Distance(PosVLoc,COM(Lats[i:i+COMPoints],Lons[i:i+COMPoints])))
        TPoints.append(Times[i+(COMPoints//2)])
        AvgMag.append(numpy.mean([abs(Mags[j][0]) for j in range(i,i+COMPoints)]))
A.plot(TPoints,COMds, color=LineColour)
A3.plot(TPoints,AvgMag, color=MagColour)
print("Centre of mass distance - average magnitude correlation:")
print(numpy.corrcoef(COMds, AvgMag))
if COMByTime:
    Label1 = "Centre"
else:
    Label1 = "Centre (" + str(COMPoints) + "-pt moving average)"
if LegendOn:
    A.legend([Label1,"Strikes"], fontsize=FontSize)
A.set_ylabel("Distance / km", fontsize=FontSize)
A3.set_ylabel("Avg Magnitude / kA", fontsize=FontSize)
A3.tick_params(labelsize=FontSize)
#---Fix labels with actual dates---
LabelPoints = [Start]
Days = End-Start
LabelPoints = [Start + (Days/(XTicks-1))*i for i in range(0, XTicks)]
StrLabels = []
if Days < 1:
    for Point in LabelPoints:
        C.execute("SELECT time(?)", (Point,))
        if AutoXTicks:
            StrLabels.append(C.fetchall()[0][0][:5])
        else:
            StrLabels.append(C.fetchall()[0][0])
    plt.xlabel("Time")
else:
    for Point in LabelPoints:
        C.execute("SELECT datetime(?)", (Point,))
        if AutoXTicks:
            StrLabels.append(C.fetchall()[0][0][:5])
        else:
            StrLabels.append(C.fetchall()[0][0])
    plt.xlabel("Date")
A.set_xticks(LabelPoints,StrLabels)
A.tick_params(labelsize=FontSize)
plt.xticks(LabelPoints,StrLabels)

if ScalePoints:
    TextOffset=0.7  #Adjust to taste
    A.scatter(Start+((Days)/90), max(Distances), s=50, color=PointColour)
    A.scatter(Start+((Days)/90), max(Distances) - (max(Distances))/18, s=10, color=PointColour)
    A.scatter(Start+((Days)/90), max(Distances) - (max(Distances))/9, s=10, color=NegColour)
    A.scatter(Start+((Days)/90), max(Distances) - 3*(max(Distances))/18, s=50, color=NegColour)
    A.text(Start+((Days)/45), max(Distances)-TextOffset, " 50kA",fontsize=FontSize)
    A.text(Start+((Days)/45), max(Distances) - (max(Distances))/18-TextOffset, " 10kA",fontsize=FontSize)
    A.text(Start+((Days)/45), max(Distances) - (max(Distances))/9-TextOffset, "-10kA",fontsize=FontSize)
    A.text(Start+((Days)/45), max(Distances) - 3*(max(Distances))/18-TextOffset, "-50kA",fontsize=FontSize)

#---

#---Histogram section of plot---
C.execute("""SELECT julianday(Date) FROM T""")
Dates = C.fetchall()
C.execute("""SELECT Lat FROM T""")
Lats = C.fetchall()
C.execute("""SELECT Lon FROM T""")
Lons = C.fetchall()
SCoordsList = [[Lats[i][0],Lons[i][0]] for i in range(0, len(Lats))]
Distances = [Distance(VLocation, i) for i in SCoordsList]
if BinByTime:
    BinCount = round((End-Start) / (BinTime / (24*60)))
    Bins = numpy.linspace(Start, End, BinCount)
    #print((End-Start) % (BinTime / (24*60)))
    #print(BinCount)
    (n,BinPoints,patches) = A2.hist([Dates[i][0] for i in range(0, len(Dates))], bins=Bins, color=BarColour)
else:
    (n,BinPoints,patches) = A2.hist([Dates[i][0] for i in range(0, len(Dates))], bins=Bins, color=BarColour)
#(n,BinPoints,patches) = A2.hist([Dates[i][0] for i in range(0, len(Dates))], bins=Bins, color=BarColour)
A2.set_ylabel("Strokes / min", fontsize=FontSize)
A2.set_xlabel("Time (UTC)", fontsize=FontSize)
A2.tick_params(labelsize=FontSize)
A2.set_xlim(left=(BinPoints[0]-(BinPoints[1]-BinPoints[0])),right=(BinPoints[-1]+2*(BinPoints[1]-BinPoints[0])))

plt.show()
