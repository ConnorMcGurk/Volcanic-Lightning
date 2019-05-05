#----------Volcanic Lightning Project----------
#Comparisons between separated volcanic and meteorological strikes

#Output:
#Figure 1 Histograms of peak current recorded in volcanic and meteorological strokes

#--Parameters--
Bins = [x for x in range(-200,205,5)]

ShowTitle = False
Title = "Stroke Energy Comparisons"

VolcColour = "red"
MetColour = "blue"

Labels = ["Kelud","Kamchatka","Bogoslof"]
FontSize = 14

ShowGrid = False
#--------------

Path1 = "C:\\Users\\Connor\\Documents\\Project\\Kelud\\Data.db"
Path2 = "C:\\Users\\Connor\\Documents\\Project\\Bezymianny\\Data.db"
Path3 = "C:\\Users\\Connor\\Documents\\Project\\Bogoslof\\Data.db"

import sqlite3
import matplotlib.pyplot as plt

VLists = []
MetLists = []

Conn = sqlite3.connect(Path1)
C = Conn.cursor()
C.execute("""SELECT Mag FROM Eruptive""")
VLists.append([M[0] for M in C.fetchall()])
C.execute("""SELECT Mag FROM Unlinked""")
MetLists.append([M[0] for M in C.fetchall()])
Conn.close()

Conn = sqlite3.connect(Path2)
C = Conn.cursor()
C.execute("""SELECT Mag FROM Volcanic""")
VLists.append([M[0] for M in C.fetchall()])
C.execute("""SELECT Mag FROM Meteorological""")
MetLists.append([M[0] for M in C.fetchall()])
Conn.close()

Conn = sqlite3.connect(Path3)
C = Conn.cursor()
C.execute("""SELECT Mag FROM Eruptive2""")
VLists.append([M[0] for M in C.fetchall()])
C.execute("""SELECT Mag FROM Met2""")
MetLists.append([M[0] for M in C.fetchall()])
Conn.close()

Fig, Axes = plt.subplots(3,2,sharex=True)
Axes[0][0].set_xlim(left=Bins[0],right=Bins[-1])

for i in range(0, len(VLists)):
    if ShowGrid:
        Axes[i][0].grid(True,axis="x")
        Axes[i][1].grid(True)
    (n, bins, patches) = Axes[i][0].hist(VLists[i],bins=Bins,color=VolcColour,label=Labels[i])
    Axes[i][1].hist(MetLists[i],bins=Bins,color=MetColour,label=Labels[i])
    Axes[i][0].text(Bins[1],max(n)*0.9,Labels[i],fontsize=FontSize)
    Axes[i][1].tick_params(labelsize=FontSize)
    Axes[i][0].tick_params(labelsize=FontSize)

Fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
plt.xlabel("Peak Current / kA",fontsize=FontSize)
plt.ylabel("Frequency",fontsize=FontSize)

if ShowTitle:
    Fig.suptitle(Title)
plt.show()
