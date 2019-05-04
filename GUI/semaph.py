from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import BooleanProperty, StringProperty, NumericProperty

from kivy.clock import Clock

from kivy.uix.widget import Widget

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from time import sleep
import time
import serial

ser = 0
ErrorDesc = "GenericError"
T = 0

STo = 0

To = 30

Nome_Macchina_1 = "Macchina_1"
Nome_Macchina_2 = "Macchina_2"
Nome_Macchina_3 = "Macchina_3"

Corre_Macchina_1 = True
Corre_Macchina_2 = True
Corre_Macchina_3 = True
Tempi = [[0,0,0],[0,0,0],[0,0,0]]


nGiri = 0

Nome_Corsa = "Corsa"

tipoPista = 1
LastGiro = 3

#funzioni per l'Arduino

SerOccupata = False             #Variabile che indica se la Seriale è o meno occupata

Tipo_Sensore = 0                #Indice del tipo di sensore in utilizzo sull arduino

Ser_To = 3000                  #Variabile con il timeout della lettura dei sensori

Ser_Tc = 500                   #Variabile con il tempo del check

Sensori_Accesi = False          #Indica se i sensori sono o meno accesi

Check_In_Lap_Settings = True  #Variabile di supporto per CheckDuringLaps

Long_Ser = False                #Variabile che impedisce la lettura della seriale per operazioni lunghe

Wait_Between_Laps = .5

UnitaMisura = 1

Ser_Soglia = 7

SerAddr = '/dev/ttyACM0'

#funzione che apre öa seriale
def OpenSer():
    global ErrorDesc
    global ser
    global SerAddr
    print("Apro la Seriale")
    try:
        ser = serial.Serial(SerAddr, 115200, timeout= 0.1)
        print("Seriale aperta correttamente")
        sleep(.2)
        ser.write("P\n".encode())
        sleep(.8)
        while ser.in_waiting:
            ser.read()
        ser.write("P\n".encode())
        sleep(.1)
        if ser.read() == b'A' :
            print("Seriale aperta correttamente")
        else:
            print("Probabile errore durante l'apertura della seriale...")
            ##Faccio qualcosa di stupido per far salire un'eccezione
            ser.close()
            ser = 0
            ser.write("ciao") #cosa stupida
        while ser.in_waiting:
            ser.read()
    except:
        print("Non riesco ad aprire la seriale")
        ErrorDesc="Non riesco a aprire la seriale"
        ser = 0

#funzione che controlla se ser è la seriale e se è aperta
def CheckSer():
    global ser
    if ser == 0:
        OpenSer()
    else:
        try:
            while ser.in_waiting:
                ser.read()
            ser.write("P\n".encode())
            sleep (.5)
            if ser.in_waiting:
                if not  ser.read() == b'A':
                    print("Errore sulla Seriale")
            while ser.in_waiting:
                ser.read()
        except:
            ser = 0
    return ser

#Funzione che scrive sulla Seriale
#In: Messaggio da scrivere sulla Seriale
#out: True if Ack recived, False else
def SerScrivi(PS, d = 10, n = 0):
    global SerOccupata
    global ser
    if SerOccupata:
        if not(PS[-1] == '\n'):
            PS = PS + "\n"
        try:
            print("Ser write")
            print(PS)
            ser.write(PS.encode())
            return SerSimpleCheck(d)
        except:
            if n == 0:
                CheckSer()
                return SerScrivi(PS,10, 1)
            return False
    else:
        return False

#Funzione che svuota la seriale
def SerFlush():
    global ser
    try:
        while ser.in_waiting:
            ser.read()
        return True
    except:
        return False

#Funzione che esegue un check rapido per controllare se Arduino ha scritto A oppure E
def SerSimpleCheck(l):
    global ser
    print("SerChekc")

    for t in range (l):
        if ser.in_waiting:
            print(t * 0.0025)
            sleep(.004)
            while ser.in_waiting:
                c = ser.read()
                c = c.decode()
                if(c == 'A'):
                    print("A")
                    #SerFlush()
                    return True
                elif (c == 'E'):
                    print("E")
                    #SerFlush()
                    return False
        sleep(.0025)
    print("To")
    return False

#Funzione che legge (se presente) 1 carattere dalla seriale
def SimpleSerRead():
    global ser
    global SerOccupata
    global Long_Ser

    if Long_Ser:
        return 0
    if SerOccupata:
        try:
            if ser.in_waiting:
                sleep(.005)
                while ser.in_waiting:
                    c = ser.read()
                    c = c.decode()
                    if not((c == ' ')or(c=='\n')or (c=='\r')):
                        return c
            return 0
        except:
            ErrorDesc = "Non riesco a leggere la seriale"
            print("Non riesco ad aprire la seriale")
            return -1
    else:
        return 0

#Funzione per prenotare la Seriale
#ritorna true se la seriale era libera e ora è stata occupata dal richiedente, falso altrimenti
def GetSer():
    global SerOccupata
    if SerOccupata:
        return False
    else:
        SerOccupata = True
        return True

#funzione che rilascia la Seriale
def LeaveSer():
    global SerOccupata
    SerOccupata = False

#funzione per gestire i messaggi piu semplici della seriale.
#Prende in ingresso il messaggio da mandare
#restituisce 1 se manda il messaggio con successo, 0 se la Seriale è occupata, -1 se avviene un errore
def EasySerMsg(msg, d = 10):
    if GetSer():
        if SerScrivi(msg, d):
            r = 1
        else:
            r = -1
        LeaveSer()
        return r
    else:
        return 0

#funzione che implementa la funnzione di Ping
def SerPing():
    return EasySerMsg("P\n")

#funzione che implementa la funnzione di Preparare i sensori
def SerPreparaSensori():
    global Sensori_Accesi
    r =  EasySerMsg("R\n")
    if(r == 1):
        Sensori_Accesi = True
    return r

#funzione che implementa la funnzione di Rilasciare i sensori
def SerRilasciaSensori():
    global Sensori_Accesi
    r = EasySerMsg("r\n")
    if(r == 1):
        Sensori_Accesi = False
    return r

#funzione che implementa la funnzione di Halt
def SerHalt(l):
    global Sensori_Accesi
    global Long_Ser

    Long_Ser = False
    LeaveSer()

    r = EasySerMsg("H\n", l)
    if(r == 1):
        Sensori_Accesi = False
    return r

#Funzione che implementa la funzione di Imposta Tipo di Sensoroi
#Controlla che il tipo passato sia valido
#Invia il tipo
#Se non ci sono errori aggiorna il tipo di sensore
def SerImpostaTipoSensori(tipo):
    try:
        tipo = int(tipo)
    except:
        #il tipo non è valido, quindi vai in Errore
        return -1
    if (tipo<0):
        #il tipo non è valido, quindi vai in Errore
        return -1
    return EasySerMsg("p" + str(tipo) + "\n")

#funzione che imposta le piste da controllare
#accetta in ingresso o una stringa con 0, 1, 2 o un array
def SerImpostaSensori(sensori):
    msg = "s"
    if ((type(sensori))==(type([])) and(len(sensori)>=3)):
        for i in range(3):
            if ((sensori[i] == True) or (sensori[i] == 1)):
                msg = msg + str(i)
    elif (type(sensori) == type("stringa")):
        for i in range(3):
            if str(i) in sensori:
                msg = msg + str(i)
    if msg == "s":
        #L'input era errato
        return -1
    else:
        print(msg)
        msg = msg + "\n"
        return EasySerMsg(msg)

#Funzione che Imposta il timeout
def SerImpostaTimeOut(tempo):
    global Ser_To
    try:
        tempo = int(tempo)
    except:
        return -1
    if(tempo<=0):
        return -1
    r = EasySerMsg("T" + str(tempo) + "\n")
    if(r == 1):
        Ser_To = tempo
    return r

#Funzione che Imposta il timecheck
def SerImpostaTimeCheck(tempo):
    global Ser_Tc
    try:
        tempo = int(tempo)
    except:
        return -1
    if(tempo<=0):
        return -1
    r = EasySerMsg("t" + str(tempo) + "\n")
    if(r == 1):
        Ser_Tc = tempo
    return r

#Funzione che Imposta la soglia
def SerImpostaSoglia(sogl):
    global Ser_Soglia
    try:
        sogl = int(sogl)
    except:
        return -1
    if(sogl<=0):
        return -1
    r = EasySerMsg("f" + str(sogl) + "\n")
    if(r == 1):
        Ser_Soglia = sogl
    return r

#Funzione per i comandi piu' lunghi
def LongSerMsg(msg):
    if GetSer():
        if SerScrivi(msg):
            return 1
        else:
            LeaveSer()
            return -1
    else:
        return 0

def SerDetect():
    return LongSerMsg("D\n")

#Funzione per comunnicare le innformazioni essenziali che devono essere passate all'Arduino al  suo avvio
def InitSer():
    global Ser_To
    global Ser_Tc
    global Tipo_Sensore
    global ErrorDesc

    lE = ""
    if not (SerImpostaTimeOut(Ser_To)==1):
        Ser_To = 0
        lE = lE + "Non riesco a impostare il Timeout\n"
    if not(SerImpostaTimeCheck(Ser_Tc)==1):
        Ser_Tc = 0
        lE = lE + "Non riesco a impostare il TimeCheck\n"
    if not(SerImpostaTipoSensori(Tipo_Sensore)==1):
        Tipo_Sensore = 0
        lE = lE + "Non riesco a impostare il Tipo di sensore\n"
    if lE == "":
        return True
    else:
        return False

#Funzione per testare la calibrazione dei sensori
def TryCheck(sensori = [1,1,1], fast = False):
    global Ser_Tc
    global Sensori_Accesi
    prec = Sensori_Accesi

    if (prec == False):
        if (fast):
            print("TryCheck chiamato con sensori non pronti")
            return -1
        r = SerPreparaSensori()
        if not(r==1):
            SerRilasciaSensori()
            return r
        sleep(.75)

    r = SerImpostaSensori([1,1,1])
    if not (r == 1):
        if not(prec):
            SerRilasciaSensori()
        return r
    r = SerImpostaTimeCheck(Ser_Tc)
    if not (r == 1):
        if not(prec):
            SerRilasciaSensori()
        return r
    r = LongSerMsg("C\n")
    if r == 1:
        sleep(Ser_Tc/1000)
        if SerSimpleCheck(20):
            LeaveSer()
            if not(prec):
                SerRilasciaSensori()
            return 1
        else:
            LeaveSer()
            if not(prec):
                SerRilasciaSensori()
            return -1
    else:
        if not(prec):
            SerRilasciaSensori()
        return r

def PreSem(piste, PassedTo = 0):
    global Ser_To
    global ErrorDesc
    global SerOccupata

    if not(SerOccupata):
        SerFlush()

    try:
        PassedTo = int(PassedTo)
    except:
        ErrorDesc = "Semaph: il parametro di timeout non è un intero"

    if ((PassedTo <= 0) and(Ser_To <=0)):
        ErrorDesc = "Semaph: TimeOut non impostato"
        return -1
    if PassedTo>0:
        r = SerImpostaTimeOut(PassedTo)
        if not (r==1):
            ErrorDesc = "Semaph: Non riesco a impostare il tempo di Timeout"
            return -1

    r = SerImpostaSensori(piste)
    if not (r==1):
        ErrorDesc="Semaph: Non riesco a selezionare le piste"
        return -1
    r = SerPreparaSensori()
    if not (r==1):
        ErrorDesc="Semaph: Non riesco a accendere i sensori"
        return -1
    r = LongSerMsg("S\n")
    if(r == 1):
        for i in range(20):
            sleep(.05)
            c = SimpleSerRead()
            if not((c == 0) or (c == 'B')):
                LeaveSer()
                if (c==-1):
                    return-1
                print("Errore nella preparazione del semaforo")
                ErrorDesc= "Semaph: Errore nella preparazione del semaforo"
                return -1
            elif (c == 'B'):
                return 1
        LeaveSer()
        print("Errore nella preparazione del semaforo: non ho letto risposta")
        ErrorDesc= "Semaph: Errore nella preparazione del semaforo"
        return -1
    else:
        print("Errore nella preparazione del semaforo: Seriale occupata o non ha riscontrato messaggio")
        ErrorDesc= "Semaph: Errore nella preparazione del semaforo"
        return -1

def SerReadDetect():
    global ser

    try:
        ser.in_waiting
    except:
        return False
    print("Leggo i tempi")
    sleep(.02)
    str0 = ser.readline()
    str1 = ser.readline()
    str2 = ser.readline()
    if (ser.in_waiting):
        if not (str0.decode()[0] == '0'):
            str0 = str1
            str1 = str2
            str2 = ser.readline()

    str0 = str0.decode()
    str1 = str1.decode()
    str2 = str2.decode()

    val = []

    if (' : ' in str0):
        val.append(str0[str0.index(' : ') + 3:])
    if (' : ' in str1):
        val.append(str1[str1.index(' : ') + 3:])
    if (' : ' in str2):
        val.append(str2[str2.index(' : ') + 3:])

    for i in range(3):
        val[i] = val[i].replace('\n', '')
        val[i] = val[i].replace('\r', '')
        if ('To' in val[i]):
            val[i] = 0
        else:
            try:
                val[i] = int(val[i])
            except:
                val[i] = 0
    print(val)
    return val

class Welcome(Screen):
    inFunz=0
    def PreRace(self, *args):
        if (self.inFunz==0):
            self.inFunz= self.inFunz +1
            if(self.inFunz == 1):
                self.race()
            else:
                print("Troppe chiamate...")

    def race(self, *args):
        if CheckSer() == 0:
            self.parent.new_Error_screen()
        else:
            if (InitSer()):
                self.parent.current = "Impostazioni"
            else:
                self.parent.new_Error_screen()

class Error(Screen):
    def ErrCode(self, *args):
        return str(ErrorDesc)

    def EndProgram(self, *args):
        quit()

class SecondScreen(Screen):
    pass

class Race(Screen):

    MacchinaInPista = [1, 2, 3]

    CM1 = BooleanProperty(Corre_Macchina_1)
    CM2 = BooleanProperty(Corre_Macchina_2)
    CM3 = BooleanProperty(Corre_Macchina_3)

    IP1 = BooleanProperty(True)
    IP2 = BooleanProperty(True)
    IP3 = BooleanProperty(True)

    TempoStart = [0, 0, 0]

    Last_Runners = ListProperty(['', '', ''])

    TempoPiste = ListProperty(["No Time","No Time", "No Time", "No Time", "No Time", "No Time","No Time", "No Time", "No Time"] )

    def Aggiorna(self, *args):
        global Nome_Macchina_1
        global Nome_Macchina_2
        global Nome_Macchina_3
        global Nome_Corsa

        if (CheckSer()==0):
            self.ids.start_button.color = (1, 0, .1, 1)
        self.ids.TitoloCorsa.text = Nome_Corsa
        self.ids.macchina_1.text= Nome_Macchina_1
        self.ids.macchina_2.text= Nome_Macchina_2
        self.ids.macchina_3.text= Nome_Macchina_3

    def SerAv(self, *args):
        global ser
        if ser == 0:
            return 0
        else:
            return 1

    def F_Nome_1(self, *args):
        global Nome_Macchina_1
        global Corre_Macchina_1
        if (Corre_Macchina_1):
            return Nome_Macchina_1
        else:
            return ""

    def F_Nome_2(self, *args):
        global Nome_Macchina_2
        if (Corre_Macchina_2):
            return Nome_Macchina_2
        else:
            return ""

    def F_Nome_3(self, *args):
        global Nome_Macchina_3
        global Corre_Macchina_3
        if (Corre_Macchina_3):
            return Nome_Macchina_3
        else:
            return ""

    def Counter(self, *args):
        global T
        global ErrorDesc
        global ser
        global STo
        global nGiri

        r = SimpleSerRead()
        #print(r)
        if (r == -1):
            Clock.unschedule(self.Counter)
            self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.stop_button.color = (1, 0, 0, 1)
            self.ids.settings_button.color= (0, 1, 0, 1)
            self.ids.start_button.color = (0, 1, 0, 1)
            self.RaiseError(ErrorDesc)
            LeaveSer()
            return
        elif (r == 'R'):
            T = -200
            self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
        elif (r=='Y'):
            T = -100
            self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
            self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
        elif(r=='G'):
            self.ids.Red_Light.bgcolor = (1, 0, 0, 1)
            self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Green_Light.bgcolor = (0, 1, 0, 1)
            self.ids.stop_button.color = (0, 1, 0, 1)
            T = 0
        elif (r=='E'):
            self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
            self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)
            print("Errore durante la calibrazione dei sensori")
            Clock.unschedule(self.Counter)
            self.ids.stop_button.color = (1, 0, 0, 1)
            self.ids.settings_button.color= (0, 1, 0, 1)
            self.ids.start_button.color = (0, 1, 0, 1)
            ErrorDesc = "Errore durante la calibrazione dei sensori"
            self.RaiseError(ErrorDesc)
            LeaveSer()
            return
        elif (r=='D'):
            LeaveSer()
            val = SerReadDetect()
            if not (val ==False):
                self.CalcolaTempi(val, nGiri)
                nGiri = nGiri + 1

        T = T+5
        if (T>=0):
            t = str(T)
        else:
            t = str(-T)
        while len(t)<5:
            t='0'+t
        self.ids.timer.text= t[0:3]+':'+t[3:5]
        if(T<=0):
            if ((T==0)and(not(self.ids.Green_Light.bgcolor[1]==1 ))):
                T = -50
                STo = STo+1
                if (STo >= 20):
                    print("No answer during Semaph")
                    ErrorDesc = "Errore sulla seriale: non ricevo risposta sul semaforo"
                    self.ids.stop_button.color = (1, 0, 0, 1)
                    self.ids.settings_button.color= (0, 1, 0, 1)
                    self.ids.start_button.color = (1, 0, 0, 1)
                    self.RaiseError(ErrorDesc)

            self.ids.timer.text = '-' + self.ids.timer.text

    def CalcolaTempi(self, val, giro):
        global tipoPista
        global LastGiro
        global Wait_Between_Laps
        global UnitaMisura

        global Tempi

        if giro == 0:
            self.MacchinaInPista = [1, 2, 3]
            for i in range(3):
                if not(val[i] ==0):
                    if i==0:
                        self.IP1 = True
                    elif i == 1:
                        self.IP2 = True
                    elif i == 2:
                        self.IP3 = True
                self.TempoStart[i] = val[i]
        else:
            for i in range(3):
                Nm = self.MacchinaInPista[i] -1
                if val[i] == 0:
                    Tempi[Nm][i] = 0
                    if Nm == 0:
                        self.IP1 = False
                    elif Nm == 1:
                        self.IP2 = False
                    elif Nm == 2:
                        self.IP3 = False
                elif (not(((Nm==0)and(self.IP1 == False))or((Nm==1)and(self.IP2 == False)) or((Nm==2)and(self.IP3==False)))):
                    print(Nm)
                    self.TempoPiste[Nm + 3*(giro-1)] = str((val[i]-self.TempoStart[Nm])/UnitaMisura)
                    Tempi[Nm][giro-1] = val[i]-self.TempoStart[Nm]
        for i in range(3):
            self.MacchinaInPista[i] = self.MacchinaInPista[i] + tipoPista
            if(self.MacchinaInPista[i] >3):
                self.MacchinaInPista[i] = 1
            elif (self.MacchinaInPista[i] <1):
                self.MacchinaInPista[i] = 3
        print("Macchina in pista")
        print(self.MacchinaInPista)
        t = False
        if not((self.IP1)or(self.IP2)or(self.IP3)):
            t = True
        if giro == LastGiro:
            print("Fine Gara")
            self.Stop()
        else:
            if t:
                print ("TimeOut")
                self.Stop()
            else:
                print("NotFinished")
                Clock.schedule_once(self.CalcolaPiste, Wait_Between_Laps)

    def CalcolaPiste(self, *args):
        global ErrorDesc
        global Check_In_Lap_Settings
        global Long_Ser

        sens = [0, 0, 0]

        if ((self.CM1)and(self.IP1)):
            for i in range(3):
                if self.MacchinaInPista[i] == 1:
                    sens[i] = 1
        if ((self.CM2)and(self.IP2)):
            for i in range(3):
                if self.MacchinaInPista[i] == 2:
                    sens[i] = 1
        if ((self.CM3)and(self.IP3)):
            for i in range(3):
                if self.MacchinaInPista[i] == 3:
                    sens[i] = 1

        print(sens)

        if not(SerImpostaSensori(sens)==1):
            ErrorDesc= "Sem: Non riesco a impostare i sensori"
            self.RaiseError(ErrorDesc)
            Clock.unschedule(self.Counter)
            return
        if Check_In_Lap_Settings:
            print("Checkinthislap")
            r = LongSerMsg("C\n")
            if (r == 0):
                ErrorDesc= "Non riesco a calibrare i sensori"
                self.RaiseError(ErrorDesc)
                Clock.unschedule(self.Counter)
                return
            elif (r == -1):
                ErrorDesc= "Non riesco a calibrare i sensori"
                self.RaiseError(ErrorDesc)
                Clock.unschedule(self.Counter)
                return
            else:
                Long_Ser = True
                Clock.schedule_once(self.CheckInLaps, Ser_Tc/1000)
        else:
            print("notCheckinthislap")
            Long_Ser = True
            Clock.schedule_once(self.CheckInLaps)
        return

    def CheckInLaps(self, *args):
        global ErrorDesc
        global Check_In_Lap_Settings
        global Long_Ser
        print("CIL")
        if (Check_In_Lap_Settings):
            print("Cazz")
            if not (SerSimpleCheck(30)):
                LeaveSer()
                ErrorDesc= "Non riesco a ricalibrarei sensori"
                self.RaiseError(ErrorDesc)
                Clock.unschedule(self.Counter)
                Long_Ser = False
                return
            Long_Ser = False
            LeaveSer()
        Long_Ser = False
        if not(SerDetect()==1):
            ErrorDesc= "Non riesco a far ripartire i sensori"
            self.RaiseError(ErrorDesc)
            Clock.unschedule(self.Counter)
        else:
            print("OK")


    def Start(self, *args):
        global ser
        global T
        global ErrorDesc
        global STo
        global nGiri

        global Nome_Macchina_1
        global Nome_Macchina_2
        global Nome_Macchina_3

        global Tempi
        global LastGiro

        for i in range(3):
            tmp = []
            for j in range(LastGiro):
                tmp.append(0)
            Tempi[i] = tmp

        nGiri = 0
        if CheckSer() == 0:
            print("Errore nell'apertura della seriale con lo start")
            ErrorDesc = "Non riesco ad aprire la seriale con lo start"
            self.RaiseError(ErrorDesc)
            return

        InitSer()

        #Seleziono le piste da ontrollare
        sens = [0, 0, 0]

        if (self.CM1):
            sens[0] = 1
        if (self.CM2):
            sens[1] = 1
        if (self.CM3):
            sens[2] = 1

        #Controlla che sia selezionata almeno una pista
        if (sens == [0, 0, 0]):
            ErrorDesc = "Non hai selezionato alcuna pista"
            self.RaiseError(ErrorDesc)
            return

        T = -300
        self.ids.stop_button.color = (.5, .5, 0, 1)
        self.ids.settings_button.color= (1, 0, 0, 1)
        self.ids.start_button.color = (1, 0, 0, 1)
        self.ids.Red_Light.bgcolor = (0, 0, 0, .9)
        self.ids.Yellow_Light.bgcolor = (0, 0, 0, .9)
        self.ids.Green_Light.bgcolor = (0, 0, 0, .9)
        r = PreSem(sens)
        if not (r == 1):
            self.ids.stop_button.color = (1, 0, 0, 1)
            self.ids.settings_button.color= (.3, .7, 0, 1)
            self.ids.start_button.color = (0, 1, 0, 1)
            if (r == -1):
                self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
                self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
                self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)
                self.RaiseError(ErrorDesc)
                return
        else:
            Clock.schedule_interval(self.Counter, 0.05)
            STo = 0
            if self.CM1:
                self.Last_Runners[0] = Nome_Macchina_1
                self.IP1 = False
            else:
                self.Last_Runners[0] = ""
            if self.CM2:
                self.Last_Runners[1] = Nome_Macchina_2
                self.IP2 = False
            else:
                self.Last_Runners[1] = ""
            if self.CM3:
                self.Last_Runners[2] = Nome_Macchina_3
                self.IP3 = False
            else:
                self.Last_Runners[2] = ""
            for i in range(9):
                self.TempoPiste[i] = ''
            self.MacchinaInPista = [1, 2, 3]



    def Stop(self, *args):
        global T
        Clock.unschedule(self.Counter)
        Clock.unschedule(self.CalcolaPiste)
        Clock.unschedule(self.CheckInLaps)
        if (SerHalt(10000) == 1):
            self.ids.start_button.color = (0, 1, 0, 1)
            self.ids.stop_button.color = (1, 0, 0, 1)
        else:
            self.ids.start_button.color = (1, 0, 0, 1)
            self.ids.stop_button.color = (0, 1, 0, 1)
        self.ids.settings_button.color= (0, 1, 0, 1)

        T = 10
        self.parent.current = 'WIN'

    def RaiseError(self,codiceErrore):
        global ErrorDesc

        print ("Errore dalla schermata Race")
        print(codiceErrore)
        ErrorDesc = codiceErrore
        Clock.unschedule(self.Counter)
        Clock.unschedule(self.CalcolaPiste)
        Clock.unschedule(self.CheckInLaps)
        self.ids.settings_button.color= (0, 1, 0, 1)
        if (SerHalt(10000) == 1):
            self.ids.start_button.color = (0, 1, 0, 1)
            self.ids.stop_button.color = (1, 0, 0, 1)
        else:
            self.ids.start_button.color = (1, 0, 0, 1)
            self.ids.stop_button.color = (0, 1, 0, 1)

        self.ids.Red_Light.bgcolor = (.9, .4, .1, 1)
        self.ids.Yellow_Light.bgcolor = (.9, .4, .1, 1)
        self.ids.Green_Light.bgcolor = (.9, .4, .1, 1)

        self.parent.new_Error_screen()


class Impostazioni(Screen):

    ValCheckSensori = NumericProperty(0)

    def on_pre_enter(self, *args):

        self.ValCheckSensori = 0

    def ControllaSensori(self, *args):
        self.ValCheckSensori = TryCheck()

    def F_Nome_C(self, *args):
        global Nome_Corsa
        return Nome_Corsa

    def Check_Nome_C(self, *args):
        global Nome_Corsa
        if (self.ids.Input_C.text == Nome_Corsa):
            self.ids.Button_Save_C.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_C.background_color=(1, 0, 0, .75)

    def Save_C(self, *args):
        global Nome_Corsa
        Nome_Corsa = self.ids.Input_C.text
        self.ids.Button_Save_C.background_color=(0, 1, 0, .75)

    def F_Nome_1(self, *args):
        global Nome_Macchina_1
        return Nome_Macchina_1

    def F_Nome_2(self, *args):
        global Nome_Macchina_2
        return Nome_Macchina_2

    def F_Nome_3(self, *args):
        global Nome_Macchina_3
        return Nome_Macchina_3

    def Check_Nome_1(self, *args):
        global Nome_Macchina_1
        if (self.ids.Input_N1.text == Nome_Macchina_1):
            self.ids.Button_Save_N1.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N1.background_color=(1, 0, 0, .75)

    def Check_Nome_2(self, *args):
        global Nome_Macchina_2
        if (self.ids.Input_N2.text == Nome_Macchina_2):
            self.ids.Button_Save_N2.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N2.background_color=(1, 0, 0, .75)

    def Check_Nome_3(self, *args):
        global Nome_Macchina_3
        if (self.ids.Input_N3.text == Nome_Macchina_3):
            self.ids.Button_Save_N3.background_color=(0, 1, 0, .75)
        else:
            self.ids.Button_Save_N3.background_color=(1, 0, 0, .75)

    def Save_N1(self, *args):
        global Nome_Macchina_1
        Nome_Macchina_1 = self.ids.Input_N1.text
        self.ids.Button_Save_N1.background_color=(0, 1, 0, .75)

    def Save_N2(self, *args):
        global Nome_Macchina_2
        self.ids.Button_Save_N2.background_color=(0, 1, 0, .75)
        Nome_Macchina_2 = self.ids.Input_N2.text

    def Save_N3(self, *args):
        global Nome_Macchina_3
        self.ids.Button_Save_N3.background_color=(0, 1, 0, .75)
        Nome_Macchina_3 = self.ids.Input_N3.text
    pass

class ColourScreen(Screen):
    colour = ListProperty([1., 0., 0., 1.])

class MyScreenManager(ScreenManager):
    def new_Error_screen(self):
        name = str(time.time())
        s = Error(name=name)
        self.add_widget(s)
        self.current = name
    pass

class MoreOptions(Screen):

    MO_TO = NumericProperty(0)
    C_MOTO = BooleanProperty(False)

    MO_TC = NumericProperty(0)
    C_MOTC = BooleanProperty(False)

    UM = NumericProperty(1)

    MO_Ser = StringProperty("")
    C_MOSer = BooleanProperty(False)
    F_MOSer = BooleanProperty(False)

    MO_WBL = NumericProperty(0)
    C_MOWBL = BooleanProperty(False)

    MO_PISTE_SEL = ListProperty([False, False, False])
    MO_PISTE_CHECKED = ListProperty([False, False, False])
    MO_CHECKING = BooleanProperty(False)
    MO_SOGLIA = ListProperty([0, 0, 0])
    MO_GEN_SOGLIA = NumericProperty(0)
    MO_SensoriAccesi = BooleanProperty(False)

    MO_CHECKED = NumericProperty(0)

    MO_CheckDuranteGara = BooleanProperty(False)

    MO_TEST_COLOR = ListProperty([(1, 0, 0, 1), (1, 1, 0, 1), (0, 1, 0, 1)])

    MOTipoPista = BooleanProperty(True)

    MO_Ngiri = StringProperty("")

    MO_Soglia = NumericProperty(8)

    def on_pre_enter(self, *args):
        self.SetMOTO()
        self.SetMOTC()
        self.SetUM()
        self.SetSer()
        self.SetWBL()
        self.SetMOPISTE()
        self.SetCheckDuranteGara()
        self.SetMOTipoPista()
        self.SetNGiri()


    def MOSaveSoglia(self, *args):
        global Ser_Soglia
        t = self.ids.In_soglia.text
        try:
            t = int(t)
        except:
            t = Ser_Soglia
        if not(t == Ser_Soglia):
            SerImpostaSoglia(t)
        self.MO_GEN_SOGLIA = Ser_Soglia
        self.ids.In_soglia.text = str(Ser_Soglia)

    def SaveNGiri(self, *args):
        global LastGiro
        t = self.ids.In_giri.text
        try:
            t = int(t)
            LastGiro = t
        except:
            pass
        self.SetNGiri()


    def SetNGiri(self, *args):
        global LastGiro
        self.MO_Ngiri = str(LastGiro)
        self.ids.In_giri.text = self.MO_Ngiri

    def SetMOTipoPista(self, *args):
        global tipoPista
        if tipoPista==1:
            self.MOTipoPista=True
        else:
            self.MOTipoPista = False

    def on_MOTipoPista(self,  *args):
        global tipoPista
        if (self.MOTipoPista):
            tipoPista = 1
        else:
            tipoPista = -1

    def MOTestLap(self, *args):
        global tipoPista
        n = [0, 0, 0]
        x = 0
        for i in range(3):
            if(tipoPista == 1):
                x = i + 1
                if(x==3):
                    x=0
                n[x] = self.MO_TEST_COLOR[i]
            elif(tipoPista == -1):
                x = i - 1
                if(x <0):
                    x = 2
                n[x] = self.MO_TEST_COLOR[i]
            else:
                n[i] = self.MO_TEST_COLOR[i]
        for i in range(3):
            self.MO_TEST_COLOR[i] = n[i]

    def MOHalt(self, *args):
        SerHalt(1000)

    def SetCheckDuranteGara(self, *args):
        global Check_In_Lap_Settings
        self.MO_CheckDuranteGara = Check_In_Lap_Settings

    def on_MO_CheckDuranteGara(self, *args):
        global Check_In_Lap_Settings
        Check_In_Lap_Settings = self.MO_CheckDuranteGara

    def SetMOTO(self, *args):
        global Ser_To
        self.MO_TO = Ser_To
        self.ids.In_To.text = str(self.MO_TO)
        self.C_MOTO = False

    def SaveTo(self, *args):
        global Ser_To
        t = self.ids.In_To.text
        try:
            t = int(t)
        except:
            t = -1
        if (t>0):
            SerImpostaTimeOut(t)

        self.ids.In_To.text = str(Ser_To)
        self.MO_TO = Ser_To
        self.C_MOTO = False
        return

    def SetMOTC(self, *args):
        global Ser_Tc
        self.MO_TC = Ser_Tc
        self.ids.In_Toc.text = str(self.MO_TC)
        self.C_MOTC = False

    def SaveTC(self, *args):
        t = self.ids.In_Toc.text
        try:
            t = int(t)
        except:
            t = -1
        if (t>0):
            SerImpostaTimeCheck(t)

        self.SetMOTC()
        self.ids.In_Toc.text = str(self.MO_TC)
        return

    def SetUM(self, *args):
        global UnitaMisura
        self.UM = UnitaMisura

    def on_UM(self, *args):
        global UnitaMisura
        UnitaMisura = self.UM

    def SetSer(self, *args):
        global SerAddr
        self.MO_Ser = SerAddr
        self.TestaSer()
        self.ids.In_ser.text = self.MO_Ser
        self.C_MOSer = False

    def SaveSer(self, *args):
        global SerAddr
        global ser

        self.MO_Ser = self.ids.In_ser.text
        SerAddr = self.MO_Ser
        self.C_MOSer = False
        try:
            ser.close()
        except:
            pass
        ser = 0

    def TestaSer(self, *args):
        if self.C_MOSer:
            self.F_MOSer = False
        else:
            if(SerPing()==1):
                self.F_MOSer = True
            else:
                self.F_MOSer = False

    def SetWBL(self, *args):
        global Wait_Between_Laps

        self.MO_WBL = Wait_Between_Laps*1000
        self.ids.In_WBL.text = str(self.MO_WBL)
        self.C_MOWBL =  False

    def SaveWBL(self, *args):
        global Wait_Between_Laps

        self.MO_WBL = self.ids.In_WBL.text
        try:
            self.MO_WBL = int(self.MO_WBL)
        except:
            self.SetWBL()
            return
        if (self.MO_WBL <0):
            self.SetWBL()
            return
        Wait_Between_Laps = self.MO_WBL/1000
        self.C_MOWBL = False

    def SetMOPISTE(self, *args):
        global Ser_Soglia
        for i in range(3):
            self.MO_PISTE_SEL[i] = False
            self.MO_PISTE_CHECKED[i] = False
            self.MO_SOGLIA[i] = 0
        self.MO_GEN_SOGLIA = Ser_Soglia
        self.MO_CHECKED = 0
        self.MO_CHECKING = False

    def MOCheck(self, *args):
        global Ser_Tc
        global ser
        self.MO_CHECKING = True
        piste = [0, 0, 0]
        if Ser_Tc <=0:
            self.MO_CHECKING = False
            return
        for i in range(3):
            self.MO_PISTE_CHECKED[i] = False
            self.MO_SOGLIA[i] = 0
            if self.MO_PISTE_SEL[i]:
                piste[i] = 1
        if not 1 in piste:
            self.MO_CHECKING = False
            return
        if not(SerImpostaSensori(piste) == 1):
            self.MO_CHECKING = False
            return
        if not(SerImpostaTimeCheck(Ser_Tc)):
            self.MO_CHECKING = False
            return
        if (LongSerMsg("Cp\n")==1):
            sleep(Ser_Tc/1000+.2)
            r = SerSimpleCheck(20)
            if ser.in_waiting:
                c = ''
                while ((not(c == 'V'))and(ser.in_waiting)):
                    c = ser.read()
                    c = c.decode()
                stri = ["", "", "", ""]
                if ser.in_waiting:
                    for i in range(3):
                        stri[i] = ser.readline()
                        stri[i] = stri[i].decode()
                if ser.in_waiting:
                    stri[3] = ser.readline()
                    stri[3] = stri[3].decode()

                print(stri)
                for i in range(3):
                    x = i
                    if not(stri[0][0] == '0'):
                        x = i + 1
                    print(stri[x])
                    try:
                        self.MO_SOGLIA[i] = int(stri[x][stri[x].index(" . ")+2:])
                    except:
                        self.MO_SOGLIA[i] = 0
            LeaveSer()
            if r:
                for i in range(3):
                    if (self.MO_PISTE_SEL[i]):
                        self.MO_PISTE_CHECKED[i]=True


        self.MO_CHECKING = False
        return

    def press(self, i):
        self.MO_PISTE_SEL[i] = not(self.MO_PISTE_SEL[i])
        self.MO_PISTE_CHECKED[1] = False
        self.MO_SOGLIA[1] = 0

    def SetMOAccesi(self, *args):
        global Sensori_Accesi
        self.MO_SensoriAccesi = Sensori_Accesi

    def MOAccendi_Spegni_Sensori(self, *args):
        global Sensori_Accesi
        if self.MO_SensoriAccesi :
            if (SerRilasciaSensori()==1):
                self.MO_SensoriAccesi = False
        else:
            if(SerPreparaSensori()==1):
                self.MO_SensoriAccesi = True

    MO_N_RETT = 0
    MO_N_CURVA = 0
    MO_N_PARAB = 0
    MO_N_SCAMBIO = 0
    MO_LEN = StringProperty("")


    def AdjRett(self, *args):
        t = self.ids.In_Rett.text
        if t=='':
            t = 0
        try:
            t = int(t)
        except:
            t = self.MO_N_RETT
            self.ids.In_Rett.text = str(t)
        self.MO_N_RETT = t
        self.CalcLen()

    def AdjCurva(self, *args):
        t = self.ids.In_Curva.text
        if t=='':
            t = 0
        try:
            t = int(t)
        except:
            t = self.MO_N_CURVA
            self.ids.In_Curva.text = str(t)
        self.MO_N_CURVA = t
        self.CalcLen()

    def AdjParab(self, *args):
        t = self.ids.In_Parab.text
        if t=='':
            t = 0
        try:
            t = int(t)
        except:
            t = self.MO_N_PARAB
            self.ids.In_Parab.text = str(t)
        self.MO_N_PARAB = t
        self.CalcLen()

    def AdjScambio(self, *args):
        t = self.ids.In_Scambio.text
        if t=='':
            t = 0
        try:
            t = int(t)
        except:
            t = self.MO_N_SCAMBIO
            self.ids.In_Scambio.text = str(t)
        self.MO_N_SCAMBIO = t
        self.CalcLen()

    def CalcLen(self, *args):
        global LastGiro
        l = 0
        l = l + 1.620 * self.MO_N_RETT
        l = l + 1.270 * self.MO_N_CURVA
        l = l + 0.618 * self.MO_N_PARAB
        l = l + 4.948 * self.MO_N_SCAMBIO
        l = l/3
        l = l * LastGiro
        print(l)
        self.MO_LEN = str(l)

class WIN (Screen):

    Classifica = ListProperty([0, 1, 2])
    CM = ListProperty([False, False, False])
    NomeMacch = ListProperty(["", "", ""])
    IP = ListProperty([False, False, False])

    def on_pre_enter(self, *args):
        self.CalcolaClassifica()

    def CalcolaClassifica(self, *args):
        global Tempi
        global Corre_Macchina_1
        global Corre_Macchina_2
        global Corre_Macchina_3
        global Nome_Macchina_1
        global Nome_Macchina_2
        global Nome_Macchina_3

        self.CM = [Corre_Macchina_1, Corre_Macchina_2, Corre_Macchina_3]
        self.NomeMacch = [Nome_Macchina_1, Nome_Macchina_2, Nome_Macchina_3]

        tmpL = [0, 0, 0]
        for i in range(3):
            tmpL[i] = Tempi[i][-1]
            self.IP[i] = True

        m = 0
        for i in range(3):
            if (tmpL[i]>m):
                m = tmpL[i]
        m = m +10
        for i in range(3):
            if ((tmpL[i] == 0)and(self.CM[i])):
                self.IP[i] = False
                tmpL[i] = m
            elif ((tmpL[i] == 0)and not(self.CM[i])):
                tmpL[i] = m+2

        t = 0
        for i in range(3):
            if (tmpL[i] < tmpL[t]):
                t = i
        self.Classifica[0] = t
        tmpL[t] = m + 5
        for i in range(3):
            if (tmpL[i] < tmpL[t]):
                t = i
        self.Classifica[1] = t
        tmpL[t] = m + 5
        for i in range(3):
            if (tmpL[i] < tmpL[t]):
                t = i
        self.Classifica[2] = t
        tmpL[t] = m + 5
        print (self.Classifica)


    pass

class WIP(Screen):
    pass

class root_widget(Widget):
    pass

class SemaphApp(App):
    pass



SemaphApp().run()
