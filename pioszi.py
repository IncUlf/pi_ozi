
# logaritmus berechnen
import tkinter as tk
import math

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  
GPIO.setup(9, GPIO.OUT)
GPIO.setup(11, GPIO.IN)

from soundplayer import SoundPlayer
import time
dev=0

step_x = 1

w=1000
h=800
nulloffset=800
faktor=0.81

zuschlag=140
wh=w/3
ltext=["10Hz","100Hz","1kHz","10kHz","20kHz"]
startstop=1
cvjob = None
freqliste=[0]*281

def startstop_callback():
    global cvjob
    if b["text"] == "Stop":
        b["text"]="Start"
        startstop=0
        if cvjob is not None:
            cv.after_cancel(cvjob)
            cvjob = None
    else:
        b["text"]="Stop"
        startstop=1
        scope(cv, 0, step_x, None)       
#ende startstop_callback()
        
#def scope(cv, x, step_x, id):
def scope(cv, x, step_x, id):
    global cvjob
    
    def measure_point():
        while not GPIO.input(11):
            GPIO.output(9, 1)
        u1=0
        u2=0
        for i in range(10000):
            if GPIO.input(11):
                GPIO.output(9, 0)
                u1=u1+faktor
                #u1=u1+1
            else:
                GPIO.output(9, 1)
                u2=u2+faktor
                #u2=u2+1
        GPIO.output(9,0)
        spannung=(nulloffset+u1-u2)/2000
        #print("Spannung: ", spannung, " u0: ",(((u1 - u2)  *  1000 / 100000) + 100))
        return spannung
    #ende measure_point()

    def dbv_coordinate(V):
        Unull=1
        if V <= 0:
            V=0.0001
        dBV=20*math.log10(V/Unull)
        if dBV < -20:
            dBV=-19.9
        elif dBV > 20:
           dBV=19.9
        #print("Spannung: ", V," dBV: ",dBV," Coord: ",(h/2-(dBV*20)))
        return (h/2-(dBV*20))
    #ende dbv_coordiante(dBV)

    def frequenz_koord(freq):
    #Dekade feststellen
        lfreq=0
        m=0
        if freq < 100:
            m=0
            lfreq=freq/10
        elif freq < 1000:
            m=1
            lfreq=freq/100
        elif freq < 10000:
            m=2
            lfreq=freq/1000
        elif freq <= 20000:
            m=3
            lfreq=freq/10000

        try:
            logwert=math.log10(lfreq)
        except:
            print ("freq: ",freq," lfreq: ",lfreq," m: ",m," logwert: ",logwert," xwert: ",xwert)
            raise
        xwert=wh*logwert+(wh*m)

        #print ("freq: ",freq," lfreq: ",lfreq," m: ",m," logwert: ",logwert," xwert: ",xwert)
        return round(xwert)
    #ende frequenz_koord(freq)
    
    if x < len(freqliste)-1:
        if id:
            last_y = cv.coords(id)[-1]
        else:
            cv.delete("line_point")
            last_y = h/2
        #x += step_x
        #Hier Ton erzeugen und dann Messen anschließend Frequenz erhoehen step_x entsprechend erhoehen
#        id = cv.create_line(x-step_x, last_y , x, measure_point()*2, fill = "black", tag="line_point", width=2)
        counter.set("Frequenz: "+str(freqliste[x]))
        old_x=0
        try:
            SoundPlayer.playTone(freqliste[x], 0.75, False, dev)
            #SoundPlayer.playTone(300, 2, False, dev)
            while SoundPlayer.isPlaying():
                #print("Warte:..",SoundPlayer.isPlaying())
                mp=measure_point()
            old_x=x-step_x
            if old_x < 0:
                old_x=0
            id = cv.create_line(frequenz_koord(freqliste[old_x]), last_y , frequenz_koord(freqliste[x]), dbv_coordinate(mp), fill = "black", tag="line_point", width=2)
            x += step_x
        except:
            print("Exception x:",x, "old_x: ",old_x)
            raise
    else:
        # hier auch Frequenz zurücksetzen
        x = 0
        id = None


#    cv.after(20, scope, cv, x, step_x, id)
    if startstop==1:
        cvjob = cv.after(20, scope, cv, x, step_x, id)
    else:
        print("Gestoppt!")
#ende scope()


#initialisieren der Frequenzliste
for n in range(0,90,1):
    freqliste[n]=n+10
for n in range(90,180,1):
    freqliste[n]=((n-90)+10)*10
for n in range(180,271,1):
    freqliste[n]=((n-180)+10)*100
for n in range(270,281,1):
    freqliste[n]=((n-270)+10)*1000

#kontrolle
#for n in range(250,len(freqliste),1):
#    print ("freqliste[",n,"]: ",freqliste[n])

#print("Laenge der Liste: ",len(freqliste))

root = tk.Tk()
root.title("Log Diagramm")
cv = tk.Canvas(root, width=w+zuschlag, height=h, bg="white")
cv.pack(padx=5, pady=5)
for n in range (40):
    cv.create_line(1, n*20, w+zuschlag, n*20, fill = "lightblue")
    cv.create_text(1,n*20,text=20-n,anchor="w")

for m in range(0,3):    
    for n in range (1,11):
        mlg=math.log10(n)
        lx=wh*mlg+(wh*m)
        #print("m: ",m," n: ",n," mlg: ",mlg," lx: ",lx)
        cv.create_line( lx, 1, lx, h, fill = "lightblue")
        if n == 1:
            cv.create_text(lx,h,text=ltext[m],anchor="sw")
#10kHz
n=2
m=3
lx=(wh*m)
#print("m: ",m," n: ",n," lx: ",lx)
cv.create_text(lx,h,text=ltext[m],anchor="sw")

#20kHz
mlg=math.log10(2)
lx=wh*mlg+(wh*m)
#print("m: ",m," n: ",n," mlg: ",mlg," lx: ",lx)
cv.create_line( lx, 1, lx, h, fill = "lightblue")

cv.create_text(lx,h,text=ltext[m+1],anchor="sw")


cv.create_line(1, h/2, w+zuschlag, h/2, fill = "lightgreen")
cv.create_text(1,h/2,text="0dBV",anchor="w")

tk.Label(root, text="Freq / 1s/Skt").pack(side=tk.RIGHT)

b = tk.Button(root, text="Stop", command=startstop_callback)
b.pack()

counter = tk.StringVar()
counter.set(0)
freq_label=tk.Label(root, width=17, textvariable=counter)
freq_label.pack( side=tk.LEFT )

cvjob = None
scope(cv, 0, step_x, None)
print ("Fertig")
tk.mainloop()