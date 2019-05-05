#----------Volcanic Lightning Project----------
#Activity report - strike association script
#Used to link lightning strokes with the period of reported activity they relate to
#Displays details of reported activity, along with recorded strokes close
#to it in time and the distance at which these occur. User can then enter
#indexes of strokes believed to be linked to activity, or 0 to indicate no
#such strokes.

InputFile = "ActivityDates.csv"

#OutputDb = "PlumeStrikeAssociation.db"
OutputFile = "PlumeStrikeAssociation.csv"

PreTolerance = 16 #hrs
PostTolerance = 38

Location = [53.9272, 168.0344]

#------------------------------------

import sqlite3, csv, math

Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

#Conn2 = sqlite3.connect(OutputFile)
#D = Conn.cursor()

def JulianDay(Date):
    """Conversion to SQLite juliandays"""
    C.execute("SELECT julianday(?)", (Date,))
    return C.fetchall()[0][0]

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

JPreT = PreTolerance / 24
JPosT = PostTolerance / 24

with open(InputFile, newline='') as F:
    with open(OutputFile, 'w') as G:
        FReader = csv.reader(F)
        GWriter = csv.writer(G, delimiter=',')
        for Line in FReader:
            Date = Line[0]
            print(Date)
            print(Line)
            C.execute("SELECT * FROM Strikes WHERE julianday(Date) BETWEEN ? AND ?", (JulianDay(Date[:10]) - JPreT,JulianDay(Date[:10])+JPosT))
            Out = C.fetchall()
            if len(Out):
                for i in range(0, len(Out)):
                    print(Out[i] + (round(Distance(Location, [Out[i][2],Out[i][3]]),1),))
                FirstNo = int(input("Index of first volcanic lightning strike:"))
                LastNo = int(input("Index of last volcanic lightning strike:"))
            else:
                FirstNo = 0
                LastNo = 0
            print([Line, FirstNo, LastNo])
            x = Line + [FirstNo] + [LastNo]
            GWriter.writerow(x)
            
