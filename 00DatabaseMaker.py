#----------Volcanic Lightning Project----------
#Database Creation Script
#V2. Uses CSV reader for more flexibility

#Data format for input file: Date Time  Lat  Lon  PeakCurrent  (NoStations)

#---Parameters---
InputFile = "Data.txt"
OutputFile = "Data.db"

Delimiter = ' '
#Adjust this to fit space or comma delimited source files

NoStationsField = True
#Set to True if input includes number of stations detecting, False otherwise

#----------------

import sqlite3, csv

#SQL connection
Conn = sqlite3.connect('Data.db')
C = Conn.cursor()

#Create Data Table
C.execute('DROP TABLE Strikes')
if NoStationsField:
    C.execute('''CREATE TABLE Strikes
    (No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL, Stations INT)''')
else:
    C.execute('''CREATE TABLE Strikes
    (No INT PRIMARY KEY, Date DATE, Lat REAL, Lon REAL, Mag REAL, Stations INT)''')


N = 1   #N is used to assign a record number to each strike

#Read in from file
with open(InputFile, newline='') as F:
    FReader = csv.reader(F, delimiter=Delimiter)
    for Line in FReader:
        if Line:    #Catch for blanks
            Values = []
            for i in range(0, len(Line)):
                if Line[i]: #Catch for excess spaces
                    Values.append(Line[i])
            if NoStationsField:
                ValuesTuple = (N,Values[0]+" "+Values[1],Values[2],Values[3],Values[4],Values[5])
                C.execute("INSERT INTO Strikes VALUES (?,?,?,?,?,?)",ValuesTuple)
            else:
                ValuesTuple = (N,Values[0]+" "+Values[1],Values[2],Values[3],Values[4])
                C.execute("INSERT INTO Strikes VALUES (?,?,?,?,?)",ValuesTuple)
            N += 1

#Print out a test example
C.execute("SELECT * FROM Strikes LIMIT 1")
print(C.fetchall())

Conn.commit()   #Save output
