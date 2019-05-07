#Importa la libreria per il logging
import logging

#Importo la libreria per i file CSV
import csv

#Variabile contenente tutti i valori di configurazione gloobali di interesse per il programma
GlobalConfig = {}

#Funzione che carica il file di configurazione indicato in path
def LoadConfigFile(path):
    global GlobalConfig

    logging.debug("LoadConfigurationFile")
    #Controlla che path sia una stringa
    if not(type(path) == type("stringa")):
        logging.error("Il parametro passato a LoadConfigurationFile non è una stringa")
        return False
    #Prova ad aprire il file in lettura
    try:
        logging.debug("LoadConfigFile: tento di aprire %s", path)
        fl = open(path, 'r')
        logging.info("%s aperto correttamente", path)
    except:
        logging.error("non riesco ad aprire il file %s", path)

    #Legge tutte le righe del file
    content = fl.readlines()
    #controlla ogni riga
    for line in content:
        #se la linea inizia con # è n commento e quindi la salta
        if line[0] == '#':
            continue
        #elimina gli accapo dalla riga
        line = line.replace('\n', '')
        #Se la linea contiene' : ' allora è da analizzare
        if ' : ' in line:
            #divido la linea in 2 parti
            linea1 = line[:line.index(' : ')]
            linea2 = line[line.index(' : ') + 3 :]

            if  ' : ' in linea2:
                tipo = linea2[:linea2.index(' : ')]
                linea2 = linea2[linea2.index(' : ') + 3:]
                if tipo == 'int':
                    try:
                        linea2 = int(linea2)
                    except:
                        logging.warning("LoadConfigFile : ho cercato di trasformare in int questo : '%s', ora %s sarà settato a 0", linea2, linea1 )
                        linea2 = 0
                elif tipo == 'bool':
                    try:
                        linea2 = bool(linea2)
                    except:
                        logging.warning("LoadConfigFile : ho cercato di trasformare in bool questo : '%s', ora %s sarà settato a False", linea2, linea1 )
                        linea2 = False

            #Aggiungo i dati letti
            GlobalConfig[linea1] = linea2
    #chiudo il file
    fl.close()
    return

#Funzione che cerca la variabile nome
#se non esiste lainserisce
def SearchGlobal(nome, expected = False):
    global GlobalConfig

    if nome in GlobalConfig:
        return GlobalConfig[nome]
    else:
        GlobalConfig[nome] = expected
        return expected

#Cerca se c'è la variabile nome in GlobalConfig
#ritorna una lista:
#ret[0] == True if Nome in GlobalConfig else False
#ret[1] == GlobalConfig[nome] if ret[0] else False
def FindGlobal (nome):
    global GlobalConfig

    if nome in GlobalConfig:
        return [True, GlobalConfig[nome]]
    else:
        return [False, False]

#Funzione simile a FindGlobal, ma ritorna False se il valore cercato non esiste, altrimenti il valore stesso
def NormFindGlobal(nome):
    return FindGlobal(nome)[1]

#Funzione che setta il valore passato a nome in GlobalConfig
def SetGlobal(nome, valore):
    global GlobalConfig

    GlobalConfig[Nome] = valore

#Funzione che imposta il valore in GlobalConfig se esisteva già in precedenza
def ReSetGlobal(nome, valore):
    global GlobalConfig

    if nome in GlobalConfig:
        GlobalConfig[nome] = valore
        return True
    return False

#Funzione che toglie un valore da GlobalConfig
def UnSetGlobal(nome):
    global GlobalConfig

    if nome in GlobalConfig:
        GlobalConfig.pop(nome)

#Funzione per salvare GlobalConfig su un file
def SaveInFile(path = ""):
    global GlobalConfig

    #Se il path non è specificato allora usa quello in GlobalConfig
    if path == '':
        c = FindGlobal("SaveOnFile")
        #Se esiste SaveOnFile, allora la usa come path
        if(c[0]):
            path = c[1]
            logging.info("Sto per salvare GlobalConfig su %s", path)
        else:
            #alrimenti risponde con errore
            logging.error("SaveInFile: nessun path specificato")
            return False

    #Controlla di poter aprire il file
    if not(CheckWriteFile(path)):
        logging.error("SaveInFile: Ho cercato di scrivere in %s, file di sola letttura", path)
        return False

    #prova ad aprire il file
    try:
        fl = open(path, 'w')
    except:
        logging.error("SaveInFile: cannot write %s file", path)

    #inserisce i valori
    for el in GlobalConfig:
        s = str(el)
        if type(GlobalConfig[el]) == type("Stringa"):
            s = s + ' : ' + GlobalConfig[el]
        elif type(GlobalConfig[el]) == type(10):
            s = s + ' : ' + 'int' + ' : ' + str(GlobalConfig[el])
        elif type(GlobalConfig[el]) == type(True):
            s = s + ' : ' + 'bool' + ' : ' + str(GlobalConfig[el])
        else:
            logging.error("SaveInFile: non riesco a salvare: %s", str(el))
            continue
        s = s + "\n"
        fl.write(s)
    #fine della scrittura
    logging.info("SaveInFile: finito")
    fl.close()
    return True

#Funzione che controlla se posso aprire il file per scriverlo
#Se inizia con "#ROnly" allora non porro scrivere
def CheckWriteFile(path):
    try:
        fl = open(path, 'r')
        l = fl.readlie()
        fl.close()
        if "#ROnly" in l:
            return False
    except:
        pass
    return True

#Funzione che salva un diczionario su un file  excel
def SaveInCSV (file, data, fieldnames):
    #Prova ad aprire il file
    try:
        csvfile = open(file, 'w')
    except:
        logging.error("Cannot open the csv file selected to write")
        return False

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for pilota in data:
        r = {}
        for header in fieldnames:
            if header in pilota:
                r[header] = str(pilota[header])
            else:
                r[header] = str("")
        writer.writerow(r)
    csvfile.close()
    return True

def ReadCSVFile(file):
    #Provo ad aprire il file
    try:
        csvfile = open(file, 'r')
    except:
        logging.error("Cannot open the csv file selected to read")
        return False
    reader =  csv.DictReader(csvfile)
    r = []
    for row in reader:
        p = {}
        for header in row:
            p[header] = row[header]
        r = r +[p]
    print(r)
    return r
