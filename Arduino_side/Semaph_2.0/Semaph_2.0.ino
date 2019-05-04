//Definnizioni globali

//Lunghezza massima messaggio
#define MAX_MSSG_LEN 20

//Massimo range di TipoSesore
#define MAX_TIPO_SENSORE 0

//Pin Luci
#define GREEN 2
#define YELLOW 3
#define RED 4


//Dichiarazione variabili globali

//Tipo di sensore
//0 -> Sensore di luce attaccato sopra
int TipoSensore = 0;

//Array delle funzioni di inizializzazione dei sensori
void (*SensorsSetupArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni di inizializzazione dei sensori
bool (*SensorsPreparaArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni di inizializzazione dei sensori
void (*SensorsRilasciaArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni di inizializzazione dei sensori
void (*SensorsResetCheckDataArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni di check dei sensori
bool (*SensorsCheckArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni di check dei sensori
bool (*SensorsDetectArray[MAX_TIPO_SENSORE+1]) ();
//Array delle funzioni per ritornare soglie dei sensori
void (*SensorsPrintSoglieArray[MAX_TIPO_SENSORE+1]) (int punt[3]);
//Array delle funzioni di Imposta soglia dei sensori
bool (*SensorsImpostaSoglieArray[MAX_TIPO_SENSORE+1]) (int s);

//Variabile con il numero di millisecondi che deve durare la lettura dei sensori prima di andare in TimeOut
unsigned int To;
//Variabile che contiene ilnumero di millisecondi che deve durare il  check dei sensori
unsigned int Tc;

//Variabile indicante l'istante dal quale si inizia la misurazione
unsigned long int TI;
//Variabili contenenti i momenti dei passagi delle macchine
unsigned long int TF[3];

//Bool che indica per ogni pista se quella pista è selezionata o meno
bool PistaSel[3];

bool SensorReady;


//Dichiarazione funzioni

//Funzione che controlla i messaggi
void HandleMessage();

//Funzione che esegue il setup del sensore selezionate
void SensorsSetup();
//Funzione che prepara il sensore
bool SensorsGetReady();
//Funzione per il rilascio dei sensori
void SensorsSetFree();
//Funzione per la cancellazione dei valori dell'ultimo check sensori
void SensorsResetCheckData();
//Funzione per il Check dei sensori
bool SensorsCheck();
//Funzione per il Detect dei sensori
bool SensorsDetect();
//Funzione per calcolare le soglie dei sensori
void SensorsPrintSoglie(int punt[3]);
//Funzione per impostare la soglia
bool SensorsImpostaSoglia(int s);

//Funzione Semaforo 
void Semaforo();
//Funzione che prepara il Semaforo (Spegne le luci)
void SemStart();

//Funzione che stampa il risultato del Detect
bool PrintResult();

//Funzione che stampa le soglie dei sensori
void PrintSoglie();

//Funzione che inizializza gli array
void InitArrays();


//Setup
void setup() {
  //Inizializzazione di tutte le variabili
  int i;
  //Settotutte le piste come non selezionate
  for (i=0; i<3; i++){
    PistaSel[i] = false;
  }
  //Imposto i sensori come rilasciati
  SensorReady = false;
  //Imposto To
  To = 0;
  //Imposto Tc
  Tc = 0;
  //Azzero TI
  TI = 0;
  //Imposto il sensore come il sensore di Default
  TipoSensore = 0;
  //Inizializzo gli array
  InitArrays();

  //Preparo i pin
  pinMode(GREEN, OUTPUT);
  pinMode(YELLOW, OUTPUT);
  pinMode(RED, OUTPUT);

  //Esecuzione delle funzioni di inizializzazione  
  SemStart();
  SensorsSetup();

  Serial.begin(115200);
}

//Funzione che esegue il Setup del sensore selezionato
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni di inizializzazione dei sensori
//               Il TipoSensore deve cadere nel giusto range
void SensorsSetup(){
  //Controlla che TipoSensore abbia senso
  if ((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return;
  }
  //Imposta il SensorReady a false
  SensorReady = false;
  //Esegue la funzione che deve eseguire
  SensorsSetupArray[TipoSensore]();
}

//Funzione per preparare i sensori
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni dei vari sensori
//                TipoSensore deve avere senso
bool SensorsGetReady(){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return false;
  }
  if(SensorsPreparaArray[TipoSensore]()){
    SensorReady = true;
    return true;
  }else{
    return false;
  }
}

//Funzione per il rilascio dei sensori
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni
//               TipoSensore deve avere senso
void SensorsSetFree(){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return;
  }
  if(SensorReady){
    SensorsRilasciaArray[TipoSensore]();
    SensorReady = false;
  }
  return;
}

//Funzione per la cancellazione dei dati relativi al check precedente dei sensori
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni
//               TipoSensore deve avere senso
void SensorsResetCheckData(){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return;
  }
  SensorsResetCheckDataArray[TipoSensore]();
  return;
}

//Funzione per il Check dei sensori
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni dei vari sensori
//                TipoSensore deve avere senso
//               Deve essere impostato il To
//                Deve essere impostato il TI
bool SensorsDetect(){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return false;
  }
  if((To<=0)||(TI<=0)){
    return false;
  }
  if(SensorsDetectArray[TipoSensore]()){
    return PrintResult();
  }else{
    return false;
  }
}

//Funzione per detectare i sensori
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni dei vari sensori
//                TipoSensore deve avere senso
//               Deve essere stato impostato il Tc
bool SensorsCheck(){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return false;
  }  
  if(Tc <= 0){
    return false;
  }
  if(SensorsCheckArray[TipoSensore]()){
    return true;
  }else{
    SensorsResetCheckData();
    Serial.println("S");
    return false;
  }
}

//Funzione per restituire le soglie
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni
//               TipoSensore deve avere senso
//               punt deve puntare a un array vuoto
void SensorsPrintSoglie(int punt[3]){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return;
  }
  (SensorsPrintSoglieArray[TipoSensore])(punt);
  return;
}


//Funzione per restituire le soglie
//Precondizione: Deve essere stato inizializzato il vettore con le funzioni
//               TipoSensore deve avere senso
//               s deve essere un valore valido per fare da soglia (
bool SensorsImpostaSoglia(int s){
  if((TipoSensore<0)||(TipoSensore>MAX_TIPO_SENSORE)){
    return false;
  }
  if(s<=0){
    return false;
  }
  return (SensorsImpostaSoglieArray[TipoSensore])(s);
}


void loop() {
  //Sec'è qualche messaggio chiama l'handler
  if(Serial.available()){
    delay(1);
    HandleMessage();
  }
  delay(1);
}

//Funzione chiamata quando un messaggio è disponibile
//Prerequisito: la seriale contiene un messaggio
//              Il messaggio termini con \n
//PostCondizione: La funzione svuota la seriale (o quantomeno fino al primo \n)
//In : null
//Out: null
void HandleMessage(){
  char buff[MAX_MSSG_LEN];
  int i = 0;

  //Leggo fino a che non trovo un '\n' o fino a un massimo di MAX_MSSG_LEN-1 caratteri
  while((Serial.available())&&(i<MAX_MSSG_LEN)){
    buff[i] = Serial.read();
    if (buff[i] == '\n'){
      buff[i] = 0;
      break;
    }
    i++;
  }
  //Se il messaggio è piu' lungo, allora si è verificato un'errore
  if (i>=MAX_MSSG_LEN){
    while(Serial.available()){
      Serial.read();
    }
    Serial.println("E");
    return;
  }

  //Letto il messaggio lo completo con uno 0 finale (al posto del '\n'
  buff[i] = 0;

  //controllo che tipo di comando è
  if(buff[0] == 'P'){
    //Se il comando è di Ping, allora rispondo con A
    Serial.println("A");
  }else if(buff[0] == 'p'){
    //Il messaggio è di tipo "imposta tipo Sensore"
    //Questo messaggio trasporta con se un byte con il tipo di sensore scelto
    if (buff[1] == 0){
      //Se il byte che contiene l'informazione non arriva, allora la comunicazione è fallita
      Serial.println("E");
      return;
    }else{
      buff[1] = buff[1] - '0'; //Calcolo il valore "intero" del sensore
      if(buff[1] > MAX_TIPO_SENSORE){
        //Se supero il range massimo del sensore è un errore
        Serial.println("E");
        return;
      }else{
        //Altrimenti il numero ottenuto è il tipo di sensore
        //Prima di Cambiare sensore rilascio l'attuale sensore
        SensorsSetFree();
        //Cambio sensore
        TipoSensore = (int)buff[1];
        //Effettua il Setup del sensore
        SensorsSetup();
        //Risponde con un Ack
        Serial.println("A");
      }
    }
  }else if (buff[0] == 's'){
    //Il comando è di tipo "Imposta Sensore"
    //Imposto tutte le piste come deselezionate
    for (i= 0; i<3; i++){
      PistaSel[i] = false;
    }
    //Controllo quali piste devo selezionare
    i=1;
    while (buff[i] != 0){
      int x = buff[i] - '0';
      if ((x>=0)&&(x<3)){
        PistaSel[x] = true;
      }
      i++;
    }
    //Rispondo con A
    Serial.println("A");
  }else if(buff[0] == 'R'){
    //Il comando è di "Prepara Sensori"
    //Preparo i Sensori
    //Se ho un problema nella preparazione dei sensori mando un errore, altrimenti un Ack
    if(SensorsGetReady()){
      Serial.println("A");
    }else{
      Serial.println("E");
    }
  }else if(buff[0] == 'r'){
    //Il comando è del tipo "Rilascia Sensori
    //rilascio i sensori
    SensorsSetFree();
    Serial.println("A");
  }else if (buff[0] == 'T'){
    //Il comando è del tipo "Imposta TimeOut"
    //Leggo il valore di TimeOut
    unsigned int tmp = 0;
    for(i = 1; buff[i] !=0; i++){
      //Leggo la cifra scritta in buff[i]
      buff[i]-='0';
      //Se è una cifra va avanti a leggere
      if ((buff[i]<0)||(buff[i]>10)){
        //Se non è una cirfa va in errore
        Serial.println("E");
        return;
      }else{
        tmp*=10;
        tmp += buff[i];
      }
    }
    //Se ha letto 0
    if (tmp == 0){
      Serial.println("E");
      return;
    }
    //Se tuto è andato a buon fine risponde con A e salva tmp al posto di To
    To = tmp;
    Serial.println("A");
  }else if (buff[0] == 't'){
    //Il comando è del tipo "Imposta TimeCheck"
    //Leggo il valore di TimeCheck
    unsigned int tmp = 0;
    for(i = 1; buff[i] !=0; i++){
      //Leggo la cifra scritta in buff[i]
      buff[i]-='0';
      //Se è una cifra va avanti a leggere
      if ((buff[i]<0)||(buff[i]>10)){
        //Se non è una cirfa va in errore
        Serial.println("E");
        return;
      }else{
        tmp*=10;
        tmp += buff[i];
      }
    }
    //Se ha letto 0
    if (tmp == 0){
      Serial.println("E");
      return;
    }
    //Se tuto è andato a buon fine risponde con A e salva tmp al posto di Tc
    Tc = tmp;
    Serial.println("A");
  }else if (buff[0] == 'C'){
    //Il comando è del tipo "Check Sensors"
    //Accetta un parametro: 'e' -> Erease -> cancella dati calibrazione precedente
    //                      'm' -> Mantain-> Mantiene i dati relativi all''ultima calibrazione
    //Se mancasse talee parametro, per default, si considera come se fosse 'm'

    //Controllo se il parametro è 'e':
    if (buff[1] == 'e'){
      //Cancello i dati relativi all'ultima calibrazione
      SensorsResetCheckData();
    }

    //Controllo che i sensori siano pronti
    if(!SensorReady){
      //Se non sono pronti li preparo
      SensorsGetReady();
    }

    //Manda un Ack per indicare di aver ricevuto il messaggio
    Serial.println("A");
    
    //Effettuo il Check
    if (SensorsCheck()){
      //Se il check va a buon fine scrivo A
      Serial.println("A");
    }else{
      //Se non va a buon fine c'è un errore 
      Serial.println("E");
    }
    //Se il messaggio è "Cp"
    if (buff[1] == 'p'){
      //Scrivi le soglie
      PrintSoglie();
    }
  }else if(buff[0] == 'D'){
    //Il comando è del tipo "Detect Pista"
    //Precondizioni: Settori preparati, controllati (non viene controllata questa condizione) e piste selezionate, TI sia stato settato
    //Controllo che i sensori siano pronti
    if(!SensorReady){
      //Se non sono pronti è un'errore
      Serial.println("E");
      return;
    }
    //controllo che almeno una pista sia selezionata
    for (i = 0; i<3; i++){
      if (PistaSel[i]){
        i = 10;
      }
    }
    if(i<10){
      Serial.println("E");
      return;
    }
    //Controllo che TI sia settato
    if(TI == 0){
      Serial.println("E");
      return;
    }

    //Mando un segnale di ack per indicare l'avvenuta ricezione del messaggio
    Serial.println("A");
    //Detecto i sensori
    if(!SensorsDetect()){
      //Se non va a buon fine vado in errore
      Serial.println("E");
      return;
    }
  }else if (buff[0] == 'S'){
    Serial.println("A");
    //Chiamo la funzione Semaforo
    Semaforo();
  }else if (buff[0] == 'H'){
    //Il comando è del tipo "Halt"
    //Spengo il semaforo
    SemStart();
    //Imposto TI a 0
    TI = 0;
    //Deseleziono tutte le piste
    for (i=0; i<3; i++){
      PistaSel[i] = false;
    }
    //Rilascio i sensori
    SensorsSetFree();

    //Scrivo A
    Serial.println("A");
  }else if (buff[0] == 'f'){
    //Il comando è del tipo "Imposta soglia"
    //Leggo il valore di soglia
    unsigned int tmp = 0;
    for(i = 1; buff[i] !=0; i++){
      //Leggo la cifra scritta in buff[i]
      buff[i]-='0';
      //Se è una cifra va avanti a leggere
      if ((buff[i]<0)||(buff[i]>10)){
        //Se non è una cirfa va in errore
        Serial.println("E");
        return;
      }else{
        tmp*=10;
        tmp += buff[i];
      }
    }
    //Se ha letto 0
    if (tmp == 0){
      Serial.println("E");
      return;
    }
    //Se tuto è andato a buon fine imposta la soglia
    if(SensorsImpostaSoglia(tmp)){
      Serial.println("A");
    }else{
      Serial.println("E");
    }
  }
}

//Funzione di preparazione del Semaforo
//(Spegne tutte le luci del semaforo
//In: null
//Out: null
void SemStart(){
  //Spengo tutte le luci
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, LOW);
}

//Funzione semaforo
//Precondizione: Devo essere nelle condizioni di fare sia check che detect
//In: null
//Out : null
void Semaforo(){
  int i;
  
  //Spengo tutte le Luci
  SemStart();
  //Scrivo B (Black)
  Serial.println("B");

  //Controllo che almeno una pista sia selezionata
  for(i=0; i<3; i++){
    if (PistaSel[i]){
      i = 10;
    }
  }
  if (i<9){
    //Nessuna pista è selezionata
    //Errore
    Serial.println("E");
    return;
  }

  //Controllo che To non sia 0
  if(To == 0){
    //Se è 0 è un errore
    Serial.println("E");
    return;
  }
  SensorsGetReady();

  //Aspetto 1 secondo
  delay(1000);
  //Accendo il rosso
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, LOW);
  digitalWrite(RED, HIGH);
  //Invia il messaggio di "Red"
  Serial.println("R");

  //Scambio Tc con 1000 (-> controllo i sensori per 1 secondo)
  i = Tc;
  Tc = 1000;

  //Resetto i dati dei sensori
  SensorsResetCheckData();

  //Eseguo il check dei sensori per 1 secondo
  if(!SensorsCheck()){
    //Se occorre un errore vado in errore
    Serial.println("EC");
    //Spengo le luci
    SemStart();
    //Reimposto Tc
    Tc = i;
    
    return;
  }

  //Accendo la luce gialla
  digitalWrite(GREEN, LOW);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Scrivo Y (->Yellow)
  Serial.println("Y");

  //Eseguo le ultime cose prima del verde:
  //Imposto TI
  TI = micros();
  //Svuoto Seriale
  while(Serial.available()){
    Serial.read();
  }

  //Controllo per 1 secondo i sensori
  //Eseguo il check dei sensori per 1 secondo
  if(!SensorsCheck()){
    //Se occorre un errore vado in errore
    Serial.println("EC");
    //Spengo le luci
    SemStart();
    //Reimposto Tc
    Tc = i;
    
    return;
  }

  //Se tutto è andato a buon fine:
  //reimposto Tc
  Tc = i;
  delay(1000);
  //Accendo il Verde
  digitalWrite(GREEN, HIGH);
  digitalWrite(YELLOW, HIGH);
  digitalWrite(RED, HIGH);
  //Scrivo G
  Serial.println("G");

  //Chiamo la funzione di detect
  SensorsDetect();
}

//Funzione che stampa il risultato del Detect
//Precondizione: L'array TF dev'essere stato riempito co dati validi
//               TI dev'essere stato inizializzato
bool PrintResult(){
  //Se TI non è stato inizializzato vai in errore 
  if( TI == 0){
    return false;
  }
  //Inizia la trasmissione
  Serial.println("D");
  //Scrive il risultato di ogni pista
  for(int i=0; i<3; i++){
    Serial.print(i);
    Serial.print(" : ");
    if(TF[i] == 0){
      //Se la pista è andata in timeout scrive To
      Serial.println("To");
    }else{
      //Altrimenti scrive la differenza di tempo tra il via e il momento in cui è scattato il sensore
      Serial.println(TF[i] - TI);
    }
  }
  return true;
}

//Funzione che scrive le soglie dei sensori
void PrintSoglie(){
  int punt[3];
  int i;

  //Calcola le soglie del sensore
  SensorsPrintSoglie(punt);

  //Stampo il risultato
  Serial.println("V");
  for (i=0; i<3; i++){
    Serial.print(i);
    Serial.print(" . ");
    Serial.println(punt[i]);
  }
}

/*******************************************************
 *    PARTE DEDICATA ALLE FUNZIONI DEI SENSORI         *
 *******************************************************/

//Definizione costanti globali per i sensori
#define LED_P_0 8
#define LED_P_1 9
#define LED_P_2 10

#define SENS_P_0 A1
#define SENS_P_1 A2
#define SENS_P_2 A3

#define Def_soglia 7

#define N_CICLI_INTERNI_DEFAULT 512

//Definizione Variabili globali dei sensori

//Variabili per il sensore di DEFAULT
//SOglie
int Av[3], Max[3], Min[3];
//Soglia
int soglia = Def_soglia;
//Pin dei sensori
int PinSensPista[3];


//Definizione funzioni dei sensori

//Sensore per i sensori di default:
//Led che fanno luce dall'alto e una fotocellula sempre in alto
//Funzione di setup
void Default_Setup();
//Funzione di Preparazione
bool Default_Prepara();
//Funzione di Check
bool Default_Check();
//Funzione di Detect
bool Default_Detect();
//Funzione di Rilascio dei sensori
void Default_Rilascia();
//Funzione per Resettare i dati dei precedenti Check
void Default_ResetCheckData();
//Funzione che ritorna le soglie dei sensori
void Default_PrintSoglie(int punt[3]);
//Funzione che imposta la soglia
bool Default_ImpostaSoglia(int s);


//Funzione che inizializza i vettori delle funzioni
//Precondizione: Tutte le funzioni siano state dichiarate prima di qui
//               La funzione venga chiamata nel setup
void InitArrays(){
  //Inizializzo gli array
  
  //Inizio dal sensore di DEFAULT
  SensorsSetupArray[0] = Default_Setup;
  SensorsPreparaArray[0] = Default_Prepara;
  SensorsRilasciaArray[0] = Default_Rilascia;
  SensorsResetCheckDataArray[0] = Default_ResetCheckData;
  SensorsCheckArray[0] = Default_Check;
  SensorsDetectArray[0] = Default_Detect;
  SensorsPrintSoglieArray[0] = Default_PrintSoglie;
  SensorsImpostaSoglieArray[0] = Default_ImpostaSoglia;
}

//Funzione di Setup del sensore di default
void Default_Setup(){
  //Imposto i pin dei led in output
  pinMode(LED_P_0, OUTPUT);
  pinMode(LED_P_1, OUTPUT);
  pinMode(LED_P_2, OUTPUT);

  //Inserisco i valori dei pin nell'array
  PinSensPista[0] = SENS_P_0;
  PinSensPista[1] = SENS_P_1;
  PinSensPista[2] = SENS_P_2;

  //Imposto soglia
  Default_ImpostaSoglia(Def_soglia);
  
  //Imposto i sensori come se fossero stati rilasciati
  Default_Rilascia();

  //Resetto i dati del sensore
  Default_ResetCheckData();
}

//Funzione che rilascia i  sensori (Spegne i led)
void Default_Rilascia(){
  //Spengo i led
  digitalWrite(LED_P_0, LOW);
  digitalWrite(LED_P_1, LOW);
  digitalWrite(LED_P_2, LOW);
}

//Funzione che cancella i dati dei precedenti Check
// -> azzera le soglie
void Default_ResetCheckData(){
  //Azzero le soglie: Av, Max, Min
  for(int i=0;i<3; i++){
    Av[i] = 0;
    Max[i] = 0;
    Min[i] = 0;
  }  
}

//Funzione che prepara i sensori (Accende le luci)
bool Default_Prepara(){
  //Accendo i led
  digitalWrite(LED_P_0, HIGH);
  digitalWrite(LED_P_1, HIGH);
  digitalWrite(LED_P_2, HIGH);

  return true;
}

//Funzione per il Check dei sensori
bool Default_Check(){
  //Dichiarazione variabili utilizzate
  unsigned long int n_cicli = 0;
  unsigned long int sum[3];
  unsigned long int T_f = millis() + Tc;
  int i, j, tmp;
  int t_max[3], t_min[3];

  //Inizializzo sum a 0
  for(i=0; i<3; i++){
    sum[i] = 0;
    t_max[i] = 0;
    t_min[i] = 2048;
  }

  //Finchè non viene interrotto dalla Seriale o dal TimeOut
  while ((Serial.available()==0)&&(millis()<T_f)){
    //Eseguo 128 letture alla volta
    for(j = 0; j<128; j++){
      n_cicli++;
      for(i=0; i<3; i++){
        //Se la pista è selezionata
        if(PistaSel[i]){
          //Leggo il valore del sensore della pista
          tmp = analogRead(PinSensPista[i]);
          //Aggiungo il valore appena letto alla somma dei valori letti da quel sensore
          sum[i] += tmp;
          //Confronto il valore appena letto con il massimo e il minimo della pista e li aggiorno
          if(tmp>t_max[i]){
            t_max[i] = tmp;
          }else if(tmp<t_min[i]){
            t_min[i] = tmp;
          }
        }
      }
    }
  }

  //Quando finisce il ciclo while:
  //Controllo i valori trovati:
  for(i=0; i<3; i++){
    if (PistaSel[i]){
      if(Av[i] == 0){
        Av[i] = sum[i] /n_cicli;

        Max[i] = (t_max[i] + Av[i] + soglia)/2;
        Min[i] = (t_min[i] + Av[i] - soglia)/2;
        
        if(t_max[i]> Av[i] + soglia){
          Av[i] = 0;
          return false;
        }
        if(t_min[i] < Av[i] - soglia){
          Av[i] = 0;
          return false;
        }
        
      }else{
        sum[i] = sum[i] / n_cicli;
        
        Max[i] = (t_max[i] + Max[i] + soglia/2)/2;
        Min[i] = (t_min[i] + Min[i] - soglia/2)/2;
        
/*        if((sum[i] > Max[i])||(sum[i] < Min[i])){
          return false;
        }        */

        Av[i] = (Av[i] + sum[i])/2;
        
/*        if((Av[i]+soglia < Max[i])||(Av[i]-soglia > Min[i])){
          Av[i] = 0;
          return false;
        }*/
      }
    }
  }
  return true;
}

//Funzione per il Detect del sensore di Default
bool Default_Detect(){
  //Momento in cui scatta il timeout
  unsigned long int t_f = millis() + To;
  //Variabile temporanea per la lettura dei sensori
  int tmp;
  //Variabile con il numero di piste ancora da controllare
  int n_piste = 0;
  //Booleano che indica il modo della pista: true se i parametri sono nella norma, false altrimenti
  bool mod[3];
  //Booleano che indica se i parametri attuali sono o meno nella norma
  bool iR;
  //Variabili di supporto
  int i, j;

  //Inizializzo il numero di piste e i paramtri delle piste
  for(i=0; i<3; i++){
    TF[i] = 0;
    if (PistaSel[i]){
      if(Av[i] == 0){
        //Vuol dire che non è stato effettuato il checkprecedentemente
        return false;
      }
      n_piste ++;   //Aggiorna numero di piste da controllare

      //Imposta il mod
      mod[i] = true;
    }
  }

  //Finchè non va in timeout e non sono disponibili caratteri da leggere 
  while ((millis()<t_f)&&(!Serial.available())){
    for(j=0; j<N_CICLI_INTERNI_DEFAULT; j++){
      //Ciclo su tutte le piste
      for(i=0;i<3;i++){
        //Se la pista non è selezionata ripeti il ciclo
        if (PistaSel[i] == true){
          //Leggo il sensore
          tmp = analogRead(PinSensPista[i]);
          //Calcolo se la lettura è nel range
          iR = ((tmp<Max[i])&&(tmp>Min[i]));
  
           //Se la iR e il mod della pistaa non sono concordi, allora è cambiata la situazione della pista
          if(mod[i] != iR){
            if(iR){
              PistaSel[i] = false;
              TF[i] = micros();
              n_piste --;
              if(n_piste == 0){
                return true;
              }
            }
            mod[i] = iR;
          }
        }
      }
    }
  }
  return true;
}

//Funzione che restituisce i valori delle soglie dei sensori
//In : Puntatore a un array di 3 elementi per salvare i risultati
//Out: Non restituisce nulla: salva nellârray quello che deve passare indietro
void Default_PrintSoglie(int punt[3]){
  int i;
  //Ciclo tra i valori delle piste e salvo la differenza del massimo e minimo
  for (i=0; i<3; i++){
    punt[i] = Max[i] - Min[i];
  }
}

//Funzione he imposta la soglia
//In : int s >0 che diventera' la nuova soglia
//Out: true se tutto ok, false else
bool Default_ImpostaSoglia(int s){
  if(s<=0){
    return false;
  }
  soglia = s;
  return true;
}
