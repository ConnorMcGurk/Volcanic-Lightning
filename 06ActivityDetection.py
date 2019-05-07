#Volcanic Lightning Project
#Test of proportion of lightning strikes close to volcanoes being associated
#with those volcanoes
#For assesing confidence in small numbers of strikes being used to detect eruptions

#Output:
#Printed values:
#   Dates and times where lightning activity begins within the distance defined
#   below of the vent

#--------Parameters--------

Location = [53.9327,168.0377]
CritDistance = 20 #km

TimeWindow = 60 #minutes

StartDate = "2013-02-01 00:00:00.000"
EndDate = "2018-02-02 00:00:00.000"

#--------------------------

import matplotlib.pyplot as plt
import math, sqlite3, numpy
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

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
SELECT * FROM Strikes WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))

Start = JulianDay(StartDate)
TStep = TimeWindow / 1440  #Conversion to days
Steps = int((JulianDay(EndDate) - Start) / TStep)
OngoingStorm = False

for i in range(0, Steps):
    LoTime = Start+(i*TStep)
    HiTime = Start+((i+1)*TStep)
    C.execute("SELECT Lat FROM T WHERE julianday(Date) BETWEEN ? AND ?", (LoTime,HiTime))
    Lats = C.fetchall()
    C.execute("SELECT Lon FROM T WHERE julianday(Date) BETWEEN ? AND ?", (LoTime,HiTime))
    Lons = C.fetchall()
    if len(Lats):
        if not(OngoingStorm):
            if Distance(Location, [Lats[0][0],Lons[0][0]]) < CritDistance:
                C.execute("SELECT datetime(?)", (HiTime,))
                print(C.fetchall()[0][0])
        OngoingStorm = True
    else:
        OngoingStorm = False

    
