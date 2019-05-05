#Volcanic Lightning project
#Stroke rate - intensity plots
#Usage note: Figure 1 (plotting stroke rate and median peak current) does not
#always render correctly initially. However, clicking the "Reset Original View"
#icon (bottom left of figure window) will cause the figure to display correctly.

#Output:
#Figure 1: Stroke rate and median peak current
#Figure 2: Stroke rate histogram
#Figure 3: Median peak current plotted against stroke rate
#Printed values:
#   Stroke Rate / Median peak current correlation coefficient
#   Number of points used in calculating correlation

#---Parameters---

#Dates to plot between:
StartDate = "2014-02-13 15:50:00.000"
EndDate = "2014-02-13 20:00:00.000"

#Coordinates of volcano [Lat,Lon]
Location = [-7.938,112.304]

AutoXTicks = True
#If True, automatically determine x axis tick positions. If False, use the number
#set below:
XTicks = 6

BinTime = 1 #Minutes. Width of bins in histogram

CorrelationCutoff = 10
#Use this to ignore median magnitudes based on less than this number of strikes
#in calculating correlations.
#Median energies based on very few strikes are more easily skewed and may be
#less representative.
BelowCutoffColour = "orange"
#Colour to plot points below this threshold in
BelowCutoffAlpha = 1
#Transparance of points below threshold

LineLabel = False
#Symbols to use in regression line equation:
YLabel = "y"
XLabel = "x"
#Decimal places to show equation to:
DP = 1

Volcanic = True
#For colour coding. Histograms will be red if this is True; blue if False

UseTitle = False
#True to show title on plots; False to hide
Title = "Kelud, " + StartDate[:10]

BoxColour = "black"
PointSize = 20
PointMarker = "."

FontSize = 16
#---------------------------------------
if Volcanic:
    BarColour = "red"
else:
    BarColour = "blue"

BinByTime = True
#Legacy variable. Currently only supporting True
#---------------------------------------
import sqlite3, math, numpy
import matplotlib.pyplot as plt
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

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

Start = JulianDay(StartDate)
End = JulianDay(EndDate)

if AutoXTicks:
    #Find a number of ticks which works to the full minute
    z = (End-Start)*24*60
    #print(z)
    for i in [5,6,4,7,3,8,9,10,2]:
        if z % (i-1) < 0.001:
            XTicks = i
            break
        

Fig1, (A, A2) = plt.subplots(2,1, gridspec_kw={'height_ratios':[2,1]}, sharex=True)
#Fig1 = plt.figure()
#A = plt.axes()
if UseTitle:
    A.set_title(Title)

BinCount = round((End-Start) / (BinTime / (24*60)))
Bins = numpy.linspace(Start, End, BinCount)
TBoxes = []
for i in range(0, len(Bins) - 1):
    #C.execute("""SELECT julianday(Date) FROM T WHERE julianday(Date) BETWEEN ? AND ?""", (Bins[i],Bins[i+1]))
    #Dates = C.fetchall()
    C.execute("""SELECT Mag FROM T WHERE julianday(Date) BETWEEN ? AND ?""", (Bins[i],Bins[i+1]))
    Mags = C.fetchall()
    TBoxes.append([math.log10(abs(Mag[0])) for Mag in Mags])

Boxplot = A.boxplot(TBoxes,positions=[(Bins[i] + (BinTime / (24*(60/BinTime)*2))) for i in range(0, len(Bins)-1)], widths=(0.8*BinTime / (24*60)), patch_artist=True)
for Patch in Boxplot['boxes']:
    Patch.set_facecolor(BoxColour)
Medians = []
for i in range(0, len(TBoxes)):
    Medians.append(numpy.median(TBoxes[i]))

#Fig2 = plt.figure()
#A2 = plt.axes()

(n, bins, patches) = A2.hist([Dates[i][0] for i in range(0, len(Dates))], bins=Bins, color=BarColour)
A2.set_xlim(left=JulianDay(StartDate),right=JulianDay(EndDate))
if UseTitle:
    A2.set_title(Title)

#This to produce histogram only
Fig4 = plt.figure()
A4 = plt.axes()
(n, bins, patches) = A4.hist([Dates[i][0] for i in range(0, len(Dates))], bins=Bins, color=BarColour)
A4.set_xlim(left=JulianDay(StartDate),right=JulianDay(EndDate))
if UseTitle:
    A4.set_title(Title)
#-------------------------------

#Dropped: Section to calculate rise time from 0 strokes to > 400
#Started = False
#TimeSince = 0
#for i in range(0, len(n)):
#    if Started:
#        TimeSince += 1
#    if n[i]:
#        Started = True
#    if n[i] > 400:
#        print(TimeSince)


#This section to remove nan values from medians
#nan (Not a Number) is added to the list when the code above tries to take
#a median of an empty set, and needs to be removed for processing
Cleann = []
CleanMedians = []
for i in range(0, len(Medians)):
    if not numpy.isnan(Medians[i]):
        Cleann.append(n[i])
        CleanMedians.append(Medians[i])


N1 = []
M1 = []
N2 = []
M2 = []
for i in range(0, len(n)):
    if n[i]:
        if n[i] > CorrelationCutoff:
            N2.append(n[i])
            M2.append(Medians[i])
        else:
            N1.append(n[i])
            M1.append(Medians[i])
#print(numpy.corrcoef(N1, M1))
#print(len(N1))

print("Median peak current - stroke rate correlation coefficient:")
print(numpy.corrcoef(N2, M2))
print("Number of points used in calculating this coefficient:")
print(len(N2))

#Plot regression line
[Gradient, Intercept] = numpy.polyfit(N2,M2,1)

#Plot
Fig3 = plt.figure()
A3 = plt.axes()
#Points:
A3.scatter(N2,M2, s=PointSize, c=BarColour, marker=PointMarker)
A3.scatter(N1,M1, s=PointSize, c=BelowCutoffColour, alpha=BelowCutoffAlpha, marker=PointMarker)
#A3.set_xlabel("Strokes/"+str(BinTime)+"min")
A3.set_xlabel("Strokes / min", fontsize=FontSize)
A3.set_ylabel("Median log(|Peak Current / kA|)", fontsize=FontSize)
#Line:
sxPoints = [min(N2), max(N2)]
syPoints = [sxPoints[i] * Gradient + Intercept for i in range(0, len(sxPoints))]
if Gradient > 0:
    Label = YLabel+" = "+str(round(Intercept,DP))+" + "+str(round(Gradient,DP))+XLabel
else:
    Label = YLabel+" = "+str(round(Intercept,DP))+" - "+str(round(abs(Gradient),DP))+XLabel
A3.plot(sxPoints, syPoints, c=BarColour, label=Label)
if LineLabel:
    A3.legend()
A3.set_xlim(left=0)
if UseTitle:
    A3.set_title(Title)

#plt.xticks([i for i in range(0, len(Bins), XTickSkips)],[Bins[i] for i in range(0, len(Bins), XTickSkips)])
#---Fix labels with actual dates---
Days = End-Start
LabelPositions = numpy.linspace(0, len(Bins),XTicks)
LabelPoints = numpy.linspace(Start, End, XTicks)
StrLabels = []
if Days < 1:
    for Point in LabelPoints:
        C.execute("SELECT time(?)", (Point,))
        if AutoXTicks:
            #Cuts off seconds, as labels have been assigned to whole minutes
            StrLabels.append(C.fetchall()[0][0][:5])
        else:
            #Includes seconds
            StrLabels.append(C.fetchall()[0][0])
    #A.set_xlabel("Time", fontsize=FontSize)
    A2.set_xlabel("Time (UTC)", fontsize=FontSize)
    A4.set_xlabel("Time (UTC)", fontsize=FontSize)
else:
    for Point in LabelPoints:
        C.execute("SELECT datetime(?)", (Point,))
        StrLabels.append(C.fetchall()[0][0])
    #A.set_xlabel("Date", fontsize=FontSize)
    A2.set_xlabel("Date", fontsize=FontSize)
    A4.set_xlabel("Date", fontsize=FontSize)
A.set_xticks(LabelPositions)
A.set_xticklabels(StrLabels)
#A.set_xticks([i for i in range(0, len(Bins), XTickSkips)])
#A.set_xticklabels([Bins[i] for i in range(0, len(Bins), XTickSkips)])
A.set_ylabel("log(|Peak Current / kA|)", fontsize=FontSize)
A2.set_xticks(LabelPoints)
A2.set_xticklabels(StrLabels)
A2.set_ylabel("Strokes / min", fontsize=FontSize)
A4.set_xticks(LabelPoints)
A4.set_xticklabels(StrLabels)
A4.set_ylabel("Strokes / min", fontsize=FontSize)
A.tick_params(labelsize=FontSize)
A2.tick_params(labelsize=FontSize)
A3.tick_params(labelsize=FontSize)
A4.tick_params(labelsize=FontSize)
plt.show()
