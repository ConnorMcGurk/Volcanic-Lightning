#Volcanic Lightning Project
#Detection Algorithm for eruptions at tropical volcanoes

#Output:
#Early Warning - lightning events beginning close to the volcano
#Eruption Detected - sustained lightning meeting conditions defined below
#Conditions beyond range - conditions breached and reason for this.
#Activity ceased - end of lightning following a warning.

#Usage note: Takes a long time to run over long time windows / with large databases.

#-----Parameters-----

Location = [3.17,98.392] #lat, lon in decimal degrees
CriticalRadius = 20    #km

CriticalTime = 90   #Minutes
MaxLocationDifference = 50  #km

TriggerThreshold = 1   #strikes / ResTime before triggering tests
ResTime = 10     #Minutes. Time step used in algorithms

QuiescenceThreshold = TriggerThreshold
#Rate which lightning must have dropped below to start tracking a new event.

RequireProximalStrikes = True
#Whether to also require that there continues to be near-vent lightning in
#an eruption, as well as tracking the centre of the cloud.
ProximalStrikeRadius = 10 #km

StartDate = "2018-02-02 00:00:00.000"
EndDate = "2018-03-01 00:00:00.000"
#Times over which to run test.

SouthernHemi = False #Fudge to cover imperfection in the centre-determining function,
#which doesn't work out + or - signs. Set True for southern hemisphere volcanoes.
#---------------------

import math, sqlite3
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

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

def DirectionDistance(Distance, Bearing, Lat,Lon):
    """Finds the new point reached by travelling Distance along Bearing from [Lat, Lon].
    Also uses haversine formula (assuming spherical Earth).
    See: https://www.movable-type.co.uk/scripts/latlong.html"""
    Lat = math.radians(Lat)
    Lon = math.radians(Lon)
    s = Distance / 6371 #6371 = Mean Earth Radius / km
    NewLat = math.asin(math.sin(Lat)*math.cos(s) + math.cos(Lat)*math.sin(s)*math.cos(Bearing))
    NewLon = Lon + math.atan2(math.sin(Bearing)*math.sin(s)*math.cos(Lat),math.cos(s)-math.sin(Lat)*math.sin(NewLat))
    return [math.degrees(NewLat),math.degrees(NewLon)]

def COM(Lats,Lons):
    """Calculates a "centre of mass" for a set of Lat,Lon points"""
    X = [Distance([0,0],[0,Lons[i]]) for i in range(0, len(Lons))]
    Y = [Distance([0,0],[Lats[i],0]) for i in range(0, len(Lons))]
    #Distance conversion is carried out to avoid distortion.
    Cx = sum(X) / len(X)
    Cy = sum(Y) / len(Y)
    if SouthernHemi:
        return [-DirectionDistance(Cy,0,0,0)[0],DirectionDistance(Cx,math.pi / 2,0,0)[1]]
    else:
        return [DirectionDistance(Cy,0,0,0)[0],DirectionDistance(Cx,math.pi / 2,0,0)[1]]

def JulianDay(ADate):
    """Converts a date into a single number matching that returned by the sqlite julianday function"""
    C.execute('''SELECT julianday(?)''', (ADate,))
    return C.fetchall()[0][0]

try:
    C.execute("DROP TABLE T")
except:
    pass
C.execute('''CREATE TABLE T
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)''')
C.execute("""INSERT INTO T
SELECT No, Date, Lat, Lon, Mag FROM Strikes WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))

TStep = ResTime / 1440  #Conversion to days
Start = JulianDay(StartDate)
Steps = int((JulianDay(EndDate) - Start) / TStep)
CritCount = CriticalTime / ResTime

#Counters for assesing algorithm performance
EarlyWarnCount = 0
EruptionDiagnosedCount = 0
CeasedCount = 0
DistanceBeyondCount = 0
NoProximalCount = 0
StormOngoing = 0

#-------------------------------------------------
#Note some redundancy in this section
C.execute("SELECT Lat FROM T WHERE julianday(Date) BETWEEN ? AND ?", (Start,Start+TStep))
Lats = C.fetchall()
C.execute("SELECT Lon FROM T WHERE julianday(Date) BETWEEN ? AND ?", (Start,Start+TStep))
Lons = C.fetchall()
ProximalStrikes = False
TimeInCount = 0
if len(Lats) >= TriggerThreshold:
    StartCentrePoint = COM([Lats[i][0] for i in range(0, len(Lats))], [Lons[i][0] for i in range(0, len(Lats))])
    if RequireProximalStrikes:
        for i in range(0, len(Lats)):
            if Distance(Location, [Lats[i][0],Lons[i][0]]) < ProximalStrikeRadius:
                ProximalStrikes = True
                break
    if (Distance(Location, StartCentrePoint) < CriticalRadius) and (ProximalStrikes or not(RequireProximalStrikes)):
        print("Early Warning")
        C.execute("SELECT datetime(?)", (HiTime,))
        print(C.fetchall()[0][0])
        TimeInCount = 1
        EarlyWarnCount += 1
    OngoingStorm = True
else:
    #LastCentrePoint = 0
    TimeInCount = 0
    OngoingStorm = False
#--------------------------------------------------


for i in range(1, Steps):
    LoTime = Start+(i*TStep)
    HiTime = Start+((i+1)*TStep)
    C.execute("SELECT Lat FROM T WHERE julianday(Date) BETWEEN ? AND ?", (LoTime,HiTime))
    Lats = C.fetchall()
    C.execute("SELECT Lon FROM T WHERE julianday(Date) BETWEEN ? AND ?", (LoTime,HiTime))
    Lons = C.fetchall()
    if len(Lats) >= TriggerThreshold:
        CentrePoint = COM([Lats[i][0] for i in range(0, len(Lats))], [Lons[i][0] for i in range(0, len(Lats))])
        if RequireProximalStrikes:
            ProximalStrikes = False
            for i in range(0, len(Lats)):
                if Distance(Location, [Lats[i][0],Lons[i][0]]) < ProximalStrikeRadius:
                    ProximalStrikes = True
                    break
        if OngoingStorm:
            StormOngoing += 1
        if TimeInCount:
            if (Distance(Location, CentrePoint) < MaxLocationDifference) and (ProximalStrikes or not(RequireProximalStrikes)):
                TimeInCount += 1
            else:
                TimeInCount = 0
                print("Conditions beyond range.")
                C.execute("SELECT datetime(?)", (HiTime,))
                print(C.fetchall()[0][0])
                print("Reason:")
                if Distance(Location, CentrePoint) > MaxLocationDifference:
                    print("Distance = " + str(round(Distance(Location, CentrePoint),3)) + " km.")
                    DistanceBeyondCount += 1
                else:
                    print("Proximal strike test = " + str(ProximalStrikes))
                    NoProximalCount += 1
        else:
            if (Distance(Location, CentrePoint) < CriticalRadius) and (ProximalStrikes or not(RequireProximalStrikes)) and not(OngoingStorm):
                print("Early Warning")
                C.execute("SELECT datetime(?)", (HiTime,))
                print(C.fetchall()[0][0])
                TimeInCount = 1
                EarlyWarnCount += 1
        OngoingStorm = True
    else:
        if TimeInCount:
            print("Activity ceased.")
            C.execute("SELECT datetime(?)", (HiTime,))
            print(C.fetchall()[0][0])
            CeasedCount += 1
        OngoingStorm = False
        TimeInCount = 0
    if TimeInCount == CritCount:
        print("---------------------------------------")
        print("Eruption diagnosed.")
        C.execute("SELECT datetime(?)", (HiTime,))
        print(C.fetchall()[0][0])
        print("---------------------------------------")
        EruptionDiagnosedCount += 1

print("Eruptions:")
print(EruptionDiagnosedCount)
print("Warnings:")
print(EarlyWarnCount)
print("Moved beyond:")
print(DistanceBeyondCount)
print("Not Proximal:")
print(NoProximalCount)
print("Ceased:")
print(CeasedCount)
print("Time in ongoing storms:")
print(StormOngoing)
print("Total time steps:")
print(Steps)
