#Volcanic Lightning Project
#Stroke energy with distance comparison

#Output:
#Figure 1: Peak currents, plotted in boxes of equal area. X axis shows maximum radial distance included in box.
#Figure 2: log(Magnitude of peak currents)
#Printed values:
#   Number of strokes
#   Peak Current - Distance Correlation
#   |Peak Current| - Distance Correlation
#   Negative Stroke Magnitude - Distance Correlation
#   Number of negative strokes
#   Positive Stroke Magnitude - Distance Correlation
#   Number of positive strokes

#--------Parameters--------

#Dates to work through (UTC)
StartDate = "2014-02-13 15:40:00.000"
EndDate = "2014-02-13 20:00:00.000"

#Coordinates of volcano [Lat,Lon]
Location = [-7.938,112.304]

#No. of distance intervals to subdivide into:
Bins = 85
SmallestR = 15 #km; smallest bin radius

ShowTitle = False
Title = "Kelud, 2014-02-13 Peak Current - Distance Relation"
PlotColour = "red"

FontSize = 20
XTickSkips = 20 #Used to limit the number of X ticks displayed.
#Increase if axis is too crowded; decrease if too sparse.
#--------------------------
import matplotlib.pyplot as plt
import math, sqlite3, numpy
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

#---Function for distance calculation---
def Distance(VCoords, SCoords):
    """Calculate the distance in km between two points given in decimal degrees.
    Uses Haversine formula, i.e. assuming perfectly spherical earth
    See: https://www.movable-type.co.uk/scripts/latlong.html for example"""
    #Convert to radians
    lon1,lat1,lon2,lat2 = map(math.radians, VCoords+SCoords)
    #Apply Haversine formula
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    #Earth radius = 6371km
    return 6371 * c

def SortTupleList(TupleList):
    """Sorts a list of tuples based on the first value in each."""
    SortedList = []
    for i in range(0, len(TupleList)):
        Pivot = len(SortedList) / 2
        while TupleList[i] < SortedList(Pivot):
            pass

#---Reduce to date of interest---
try:
    C.execute("DROP TABLE T")
except:
    pass
C.execute('''CREATE TABLE T
(No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL)''')
C.execute("""INSERT INTO T
SELECT * FROM Strikes WHERE Date BETWEEN ? AND ?""", (StartDate,EndDate))

#Get data lists from SQL
C.execute("""SELECT julianday(Date) FROM T""")
Dates = C.fetchall()
C.execute("""SELECT Lat FROM T""")
Lats = C.fetchall()
C.execute("""SELECT Lon FROM T""")
Lons = C.fetchall()
C.execute("""SELECT Mag FROM T""")
Mags = C.fetchall()
SCoordsList = [[Lats[i][0],Lons[i][0]] for i in range(0, len(Lats))]
Distances = [Distance(Location, i) for i in SCoordsList]

BinDistances = [SmallestR]
DistLists = []
LogMagDistLists = []
for i in range(0, Bins):
    BinDistances.append(math.sqrt(BinDistances[i]**2 + BinDistances[0]**2))
    DistLists.append([])
    LogMagDistLists.append([])

for i in range(0, len(Distances)):
    j = 0
    while Distances[i] > BinDistances[j]:
        j += 1
    DistLists[j].append(Mags[i][0])
    LogMagDistLists[j].append(math.log10(abs(Mags[i][0])))

print("No. Strokes:")
print(len(Mags))
print("Peak Current - Distance correlation:")
print(numpy.corrcoef([Mags[i][0] for i in range(0, len(Mags))], Distances))
print("|Peak Current| - Distance correlation:")
print(numpy.corrcoef([abs(Mags[i][0]) for i in range(0, len(Mags))], Distances))

#print(numpy.corrcoef([Mags[i][0] for i in range(0, len(Mags))], [Lats[i][0] for i in range(0, len(Lats))]))
#print(numpy.corrcoef([abs(Mags[i][0]) for i in range(0, len(Mags))], [Lats[i][0] for i in range(0, len(Lats))]))
#print(numpy.corrcoef([Mags[i][0] for i in range(0, len(Mags))], [Lons[i][0] for i in range(0, len(Lons))]))
#print(numpy.corrcoef([abs(Mags[i][0]) for i in range(0, len(Mags))], [Lons[i][0] for i in range(0, len(Lons))]))

#RMags = []
#AbsRMags = []
#RDists = []
TupleList = []
PosMagDists = []
PosMags = []
NegMagDists = []
NegMags = []
for i in range(0, len(Mags)):
    #if Distances[i] > 20:
        #RMags.append(Mags[i][0])
        #RDists.append(Distances[i])
        #TupleList.append((RMags, RDists))
        #AbsRMags.append(abs(Mags[i][0]))
    if Mags[i][0] > 0:
        PosMags.append(Mags[i][0])
        PosMagDists.append(Distances[i])
    else:
        NegMags.append(abs(Mags[i][0]))
        NegMagDists.append(Distances[i])

#print(TupleList)
#print(TupleList.sort())

#print(numpy.corrcoef(RMags, RDists))
#print(len(RMags))
#print(numpy.corrcoef(AbsRMags, RDists))

print("Negative Stroke Magnitude - Distance Correlation:")
print(numpy.corrcoef(NegMags, NegMagDists))
print("No. Negative Strokes:")
print(len(NegMags))
print("Positive Stroke Magnitude - Distance Correlation:")
print(numpy.corrcoef(PosMags, PosMagDists))
print("No. Positive Strokes:")
print(len(PosMags))

#plt.scatter(RMags, RDists, s=1)
#plt.figure()
#plt.scatter([Mags[i][0] for i in range(0, len(Mags))], Distances, s=1, c=PlotColour)
#plt.figure()
#plt.scatter([abs(Mags[i][0]) for i in range(0, len(Mags))], Distances, s=1, c=PlotColour)
#plt.xlabel("Distance / km")
#plt.ylabel("Peak Current")
#if ShowTitle:
#    plt.title(Title)

plt.figure()
plt.boxplot(DistLists)
plt.xticks([i for i in range(1, Bins, XTickSkips)],[round(BinDistances[i],1) for i in range(0,Bins,XTickSkips)])
plt.xlabel("Max Distance / km")
plt.ylabel("Peak Current")
if ShowTitle:
    plt.title(Title)
plt.figure()
Ax1 = plt.axes()
plt.boxplot(LogMagDistLists)
plt.xticks([i for i in range(1, Bins, XTickSkips)],[round(BinDistances[i],1) for i in range(0,Bins,XTickSkips)], fontsize=FontSize)
Ax1.yaxis.set_tick_params(labelsize=FontSize)
plt.xlabel("Distance / km", fontsize=FontSize)
plt.ylabel("log(|Peak Current|)", fontsize=FontSize)
if ShowTitle:
    plt.title(Title)
plt.show()
