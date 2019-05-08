#Programma per il semaforo delle mini 4 WD
#Sviluppato da Giorgio Corbetta
#per info scrivere a: giorgiocor98@gmail.com

#Libreria per il log
import logging

#Modulo per gestire i file e le variabili globali
import Sem_files as glb

#Importo le librerie di kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import BooleanProperty


#Variabile con il path del file con le configurazioni da caricare
FileSetting_Path = "./d_files/Setting/LoadFile.dat"

#Stack con le schermate aperte
StckScherm = ["welcome"]

#funzione iniziale
def main():
    #avvio Il log sul file indicato
    logging.basicConfig(filename='./d_files/log/example.log',level=logging.DEBUG)
    logging.info('Programma avviato')

    #Carica file con le configurazioni
    glb.LoadConfigFile(FileSetting_Path)

    #Facccio partire la parte grafica
    SemaforoApp().run()

#funzione per uscire dal programma
#Accetta un bool come parametro impostato per default a True
#Se il parametro è  True allora controlla se deve salvare, altrimenti lasia l'esecuzione
def PrgExit(Save = True):
    logging.debug("sto per finire esecuzione")
    #Controlla il parametro passato
    if(Save == True):
        #Se impostato il salvataggio automatico lo eseguo
        if (glb.NormFindGlobal("AutoSalvataggio") == True):
            logging.debug("AutoSalvataggio impostato: lo eseguo")
            glb.SaveInFile()
    logging.info("Fine esecuzione")
    quit()

#funzione che controlla ed eventualmente inserisce in cima alla pila il nomeSchermata
def CheckStack(nomeSchermata):
    global StckScherm

    if not(StckScherm[-1] == nomeSchermata):
        StckScherm = StckScherm + [nomeSchermata]
    return

#Funzione che aggiunge allo stack il nome nomeSchermata
# Ritorna False se la schermata nello stack, altrimenti True
#Porta la schermata in cima
def AddToStack(nomeSchermata):
    global StckScherm

    if not (nomeSchermata in StckScherm):
        StckScherm = StckScherm + [nomeSchermata]
        return True
    else:
        StckScherm = StckScherm[:StckScherm.index(nomeSchermata)] + StckScherm[:StckScherm.index(nomeSchermata) + 1]
        return False


def RandomizeArray (arr):
    return arr

#Inizia la parte di codice che serve per la gestione della parte grafica

class SemaforoApp(App):
    pass

class MyScreenManager(ScreenManager):

    #Funzione che passa crea una nuova schermata OrganizzaGara
    def Nuova_Schermata_OrganizzaGara(self):
        if (AddToStack("OrganizzaGara") == True):
            logging.debug("Creo una nuova schermata OrganizzaGara")
            s = OrganizzaGara()
            self.add_widget(s)
        else:
            logging.debug("è già presente la schermata cercata")
        self.current = 'OrganizzaGara'
        logging.debug("Passo alla schermata OrganizzaGara")
        return True
    pass

class Home(Screen):

    #Funzione che Termina l'esecuzione
    def Leave(self, *args):
        #Chiama la funzione di default
        PrgExit()

    #Funzione che va alla schermata di organizza OrganizzaGara
    def GoToOrganizzaGara(self, *args):
        #chiama la funzione per cambiare schermata
        self.parent.Nuova_Schermata_OrganizzaGara()

    pass

class OrganizzaGara(Screen):

    #Variabile per attivare il pulsante di Carica del File Piloti
    #CaricaFPButtDisabled = BooleanProperty(True)
    #Variabile per attivare il pulsante di Salva del File Piloti
    SalvaFPButtDisabled = BooleanProperty(True)

    #Variabile per indicare stato di apertura Iscrizioni
    IscrizioniAperte = BooleanProperty(True)

    #Lista dei piloti partecipanti alla gara
    ListaPiloti = []

    init_index = 0

    #Funzione eseguita al caricamento della schermata
    def on_pre_enter(self, *args):
        #Controlla lo stack delle schermate
        CheckStack("OrganizzaGara")

        self.ScriviPiloti()

        #Funzione che restituisce il nome del pilota in posizione richiesta
    def GetNomePilotaInPos(self, posizione, init_index):
        #Se la lista è vuota non scrive nulla
        if len(self.ListaPiloti) == 0:
            return ""
        #Fa ruotare la lista
        posizione = posizione + init_index
        if (len(self.ListaPiloti) <= posizione):
            posizione = posizione- len(self.ListaPiloti)
            #Se sto rifacendo il giro ritorna ""
            if (posizione >= init_index):
                return ""
        #ritorna la posizione richiesta
        return self.ListaPiloti[posizione]['nome']

    #Funzione che scrive la lista dei Piloti
    def ScriviPiloti(self, *args):
        #Per ogni label scrive il corrispettivo pilota
        self.ids.Lab_P_1.text = self.GetNomePilotaInPos(0, self.init_index)
        self.ids.Lab_P_2.text = self.GetNomePilotaInPos(1, self.init_index)
        self.ids.Lab_P_3.text = self.GetNomePilotaInPos(2, self.init_index)
        self.ids.Lab_P_4.text = self.GetNomePilotaInPos(3, self.init_index)
        self.ids.Lab_P_5.text = self.GetNomePilotaInPos(4, self.init_index)
        self.ids.Lab_P_6.text = self.GetNomePilotaInPos(5, self.init_index)
        self.ids.Lab_P_7.text = self.GetNomePilotaInPos(6, self.init_index)
        self.ids.Lab_P_8.text = self.GetNomePilotaInPos(7, self.init_index)
        self.ids.Lab_P_9.text = self.GetNomePilotaInPos(8, self.init_index)
        self.ids.Lab_P_10.text = self.GetNomePilotaInPos(9, self.init_index)

    #Funzione che cerca il nuovo indice per matcharre al meglio la ricerca
    def SearchNewIndex(self, *args):
        #Legge il nome inserito
        nome = self.ids.In_Pilota.text
        #Se non è stato inserito alcun nome salta
        if nome == "":
            return False
        #Cerca il primo nome che matchi
        tmp = len(nome)
        t_index = self.init_index
        for i in range(len(self.ListaPiloti)):
            if nome == self.ListaPiloti[i]['nome'][:tmp]:
                t_index = i
        if not(self.init_index == t_index):
            self.init_index=t_index
            return True
        else:
            return False

    #Funzione che aggiorna la lista dei Piloti
    def AggiornaTestoPilota(self, *args):
        #Se il ttesto finisce con un accapo lo prende come un tentativo di AutoSalvataggio
        if self.ids.In_Pilota.text == "":
            return
        if self.ids.In_Pilota.text[-1]=='\n':
            self.ids.In_Pilota.text= self.ids.In_Pilota.text[:-1]
            self.AggiungiPilota()
            self.init_index = len(self.ListaPiloti)-1
            self.ScriviPiloti()
        else:
            #Ricalcola l'init_index
            if self.SearchNewIndex():
                self.ScriviPiloti()

    #Funzione che restituisce il nome del file su cui salvare
    def GetFilePiloti(self, *args):
        return glb.SearchGlobal("FilePiloti", "corsa.csv")

    #Funzione che aggiunge il pilota nella lista Piloti
    def AggiungiPilota(self, *args):
        #Recupera il nome del pilota
        nomeP = self.ids.In_Pilota.text
        if nomeP == "":
            return
        logging.debug("Aggiungo %s alla listaPiloti", nomeP)

        #Cerca se il pilota è gia nella Lista
        ins = False
        if self.NotInListaPiloti(nomeP):
            print("::")
            for i in range(len(self.ListaPiloti)):
                if nomeP<self.ListaPiloti[i]['nome']:
                    print (self.ListaPiloti[i]['nome'] )
                    self.ListaPiloti = self.ListaPiloti[:i] + [{'nome':nomeP}] + self.ListaPiloti[i:]
                    self.init_index = i
                    ins = True
                    break
            if not ins:
                self.ListaPiloti = self.ListaPiloti + [{'nome':nomeP}]

        #imposta testo di In_Pilota a ""
        self.ids.In_Pilota.text = ""

        #Attiva pulsante di salvataggio
        self.SalvaFPButtDisabled = False

        #Printa lista
        print(self.ListaPiloti)
        self.ScriviPiloti()

    def CallCalcolaManches(self, *args):
        self.CalcolaManches(6, self.ListaPiloti, "")

    #Funzione che calcola le manches
    def CalcolaManches(self, n_manches, Piloti, PathFile):
        #Prepro il vettore dei Piloti
        MPiloti = []
        Manches = []
        for i in Piloti:
            MPiloti.append({'nome': i['nome'], 'P1' : 0, 'P2': 0, 'P3' : 0})

        for i in range(n_manches):
            Pista1 = ['P1']
            Pista2 = ['P2']
            Pista3 = ['P3']
            PisteArr = [Pista1, Pista2, Pista3]
            MaxPista = int(len(MPiloti)/3) + 1
            print("Max")
            print (MaxPista)
            while(len(MPiloti)>0):
                for x in PisteArr:
                    if ((len(x)<=(MaxPista)and(len(MPiloti)>0))):
                        print ("L")
                        print(int((i+1)/n_manches))
                        if MPiloti[0][x[0]] <= int((i+1)/3):
                            x.append(MPiloti.pop(0))

            for i in range(len(PisteArr)):
                print("Pista %d", i)
                PisteArr[i] = RandomizeArray(PisteArr[i])
                print(PisteArr[i])

            Manche_x = []

            for i in range(MaxPista):
                corsa = []
                j = i+1
                for x in PisteArr:
                    if (len(x) >= j+1):
                        x[j][x[0]] = x[j][x[0]] + 1
                        corsa.append(x[j])
                        MPiloti.append(x[j])
                    else:
                        corsa.append({'nome' : ''})
                print(corsa)
                Manche_x.append(corsa)
            Manches.append(Manche_x)

            print (MPiloti)

        print (Manches)
        print(len(Manches))



    #Funziono che elimina il pilota dalla lista
    def EliminaPilota(self, id):
        if id >= len(self.ListaPiloti):
            id = id - len(self.ListaPiloti)

        self.ListaPiloti.pop(id)
        self.ScriviPiloti()

    #Funzione che cerca se nella lista c'è un Pilota con stesso Nome
    def NotInListaPiloti(self, nome):
        if nome == "":
            return False
        for pilota in self.ListaPiloti:
            if nome == pilota['nome']:
                return False
        return True

    #Funzione che salva la lista dei piloti su un file
    def SalvaFilePiloti(self, *args):
        filename = glb.FindGlobal('FilePiloti')[1]
        filePath = glb.FindGlobal('PathFilePiloti')[1]
        filename = filePath + filename
        print (filename)
        glb.SaveInCSV(filename, self.ListaPiloti, ["nome", "T1"])

    #Funzione che carica la lista dei piloti da un file
    def CaricaFilePiloti(self, *args):
        filename = glb.FindGlobal('FilePiloti')[1]
        filePath = glb.FindGlobal('PathFilePiloti')[1]
        filename = filePath + filename
        self.ListaPiloti = glb.ReadCSVFile(filename)
        self.ScriviPiloti()



main()
