#Volcanic Lightning project
#Matching between WWLLN and Vaisala recorded strikes

#Output:
#Figure 1: Scatter plot of GLD360 peak current magnitude and WWLLN energy for
#   matched strokes
#Figure 2: Scatter plot of matched stroke positions
#Figure 3: Histogram of matched strokes by the distance separating them in 1km bins
#Printed values:
#   Number of matched strokes with given conditions
#   Correlation coefficient between GLD360 peak current magnitude and WWLLN
#       energy for matched strokes
#   Mean distance error between matched strokes
#   Median distance error between matched strokes
#   Number of duplicate matches

#Note that it is possible for multiple strokes to match each other under the
#given criteria, and where this the closest matching pair will be counted.

#Parameters
StartDate = "2014-02-13 15:30:00.000"
EndDate = "2014-02-13 20:10:00.000"

TimeErrorStep = 0.001 #Sec
DistanceError = 5 #km

FontSize = 14
#-----------
import matplotlib.pyplot as plt
import sqlite3, numpy, math

#def JulianDay(ADate):
#    """Converts a date into a single number matching that returned by the sqlite julianday function"""
#    C.execute('''SELECT julianday(?)''', (ADate,))
#    return C.fetchall()[0][0]

#---Function for distance calculation---
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

TimeError = TimeErrorStep / (24*60*60)

#Fetch WWLLN Data---------------------
Conn = sqlite3.connect('C:\\Users\\Connor\\Documents\\Project\\WWLLN\\Kelud\\Data.db')
C = Conn.cursor()

C.execute("SELECT julianday(Date) FROM Volcanic WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
LLNTimes = C.fetchall()

C.execute("SELECT Mag FROM Volcanic WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
LLNMags = C.fetchall()

C.execute("SELECT Lat, Lon FROM Volcanic WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
LLNPos = C.fetchall()

C.execute("SELECT EnErr FROM Volcanic WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
EnErr = C.fetchall()

Conn.close()
#--------------------------------------

#Fetch Vaisala Data--------------------
Conn = sqlite3.connect('C:\\Users\\Connor\\Documents\\Project\\Kelud\\Data.db')
C = Conn.cursor()

C.execute("SELECT julianday(Date) FROM Eruptive WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
VTimes = C.fetchall()

C.execute("SELECT Mag FROM Eruptive WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
VMags = C.fetchall()

C.execute("SELECT Lat, Lon FROM Eruptive WHERE Date BETWEEN ? AND ?", (StartDate, EndDate))
VPos = C.fetchall()
#--------------------------------------
LLNCount = len(LLNTimes)
VCount = len(VTimes)

Limit = min(LLNCount, VCount)

#LastDate = JulianDay(StartDate)
#End = JulianDay(EndDate)

LLNi = 0
Vi = 0

VM = []
LLNM = []

VLat = []
VLon = []
LLNLat = []
LLNLon = []
LLNEnErr = []

VSTimes = []
LLNSTimes = []

#Old (computationally light, but potentially inaccurate) method
#while LLNi < LLNCount and Vi < VCount:
#    LLNT = LLNTimes[LLNi][0]
#    VT = VTimes[Vi][0]
#    if VT < (LLNT + TimeError) and (VT + TimeError) > LLNT:
#        if Distance([VPos[Vi][0],VPos[Vi][1]],[LLNPos[LLNi][0],LLNPos[LLNi][1]]) < DistanceError:
#            print(LLNT)
#            C.execute("SELECT datetime(?)", (VT,))
#            print(C.fetchall()[0][0])
#            if not LLNMags[LLNi][0] == 0:
#                VM.append(VMags[Vi][0])
#                LLNM.append(LLNMags[LLNi][0])
#            VLat.append(VPos[Vi][0])
#            VLon.append(VPos[Vi][1])
#            LLNLat.append(LLNPos[LLNi][0])
#            LLNLon.append(LLNPos[LLNi][1])
#            Vi += 1
#            LLNi += 1
#        else:
#            if VT = VTimes[Vi+1]:
#                pass
#    else:
#        if LLNT > VT:
#            Vi += 1
#        else:
#            LLNi += 1

j = 0
print(LLNTimes[0][0])
Distances = []
for i in range(0, len(VTimes)):
    VT = VTimes[i][0]
    Break = False
    LLNT = LLNTimes[j][0]
    while (LLNT + TimeError) > VT and j > 0:
        j = j - 1
        LLNT = LLNTimes[j][0]    
    while (LLNT - TimeError) < VT and j < (len(LLNTimes)-1):
        if VT < (LLNT + TimeError) and (VT + TimeError) > LLNT:
            if Distance([VPos[i][0],VPos[i][1]],[LLNPos[j][0],LLNPos[j][1]]) < DistanceError:
                if not LLNMags[j][0] == 0:
                    VM.append(VMags[i][0])
                    LLNM.append(LLNMags[j][0])
                    LLNEnErr.append(EnErr[j][0])
                VSTimes.append(VT)
                LLNSTimes.append(LLNT)
                VLat.append(VPos[i][0])
                VLon.append(VPos[i][1])
                LLNLat.append(LLNPos[j][0])
                LLNLon.append(LLNPos[j][1])
                Distances.append(Distance([VPos[i][0],VPos[i][1]],[LLNPos[j][0],LLNPos[j][1]]))
        j += 1
        LLNT = LLNTimes[j][0]

DeleteList = []
for i in range(0, len(VSTimes)-1):
    if VSTimes[i] == VSTimes[i+1] and VLat[i] == VLat[i+1] and VLon[i] == VLon[i+1]:
        if Distance([VLat[i],VLon[i]],[LLNLat[i],LLNLon[i]]) < Distance([VLat[i+1],VLon[i+1]],[LLNLat[i+1],LLNLon[i+1]]):
            DeleteList.append(i+1)
        else:
            DeleteList.append(i)
for i in range(0, len(LLNSTimes)-1):
    if LLNSTimes[i] == LLNSTimes[i+1] and LLNLat[i] == LLNLat[i+1] and LLNLon[i] == LLNLon[i+1]:
        if Distance([VLat[i],VLon[i]],[LLNLat[i],LLNLon[i]]) < Distance([VLat[i+1],VLon[i+1]],[LLNLat[i+1],LLNLon[i+1]]):
            DeleteList.append(i+1)
        else:
            DeleteList.append(i)

print("Number of duplicate records:")
print(len(DeleteList))

VM2 = []
LLNM2 = []
LLNEnErr2 = []
VLon2 = []
VLat2 = []
LLNLon2 = []
LLNLat2 = []
Distances2 = []
for i in range(0,len(VM)):
    if i not in DeleteList:
        VM2.append(VM[i])
        LLNM2.append(LLNM[i])
        LLNEnErr2.append(LLNEnErr[i])
        VLon2.append(VLon[i])
        VLat2.append(VLat[i])
        LLNLon2.append(LLNLon[i])
        LLNLat2.append(LLNLat[i])
        Distances2.append(Distances[i])
    
print("Matched strokes:")
print(len(VM2))
print("GLD360 peak current magnitude - WWLLN energy correlation coefficient:")
print(numpy.corrcoef([abs(M) for M in VM2], LLNM2))

Ax = plt.axes()
Ax.errorbar(VM2, LLNM2, yerr=LLNEnErr2, linestyle="None", capsize=3, marker="x")
Ax.set_xlabel("Peak Current (GLD360)", fontsize=FontSize)
Ax.set_ylabel("Stroke Energy (WWLLN)", fontsize=FontSize)
Ax.set_ylim(bottom=0)
Ax.tick_params(labelsize=FontSize)

print("Mean distance error: " + str(round(numpy.mean(Distances2),1)) + " km")
print("Median distance error: " + str(round((numpy.median(Distances2)),1)) + " km")

plt.figure()
plt.scatter(VLon2,VLat2, s=1)
plt.scatter(LLNLon2,LLNLat2, s=1)

plt.figure()
Ax2 = plt.axes()
Ax2.hist(Distances2, bins=DistanceError)
Ax2.set_xlabel("Distance / km", fontsize=FontSize)
Ax2.set_ylabel("Frequency Density", fontsize=FontSize)
Ax2.tick_params(labelsize=FontSize)
plt.show()
