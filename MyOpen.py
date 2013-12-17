#!/usr/bin/python

######################################################################
### Libreria MyOpen ### Connessione a gateway MyOpenWebNet Bticino ###
######################################################################
# Autore: Fernando Figaroli - FerX
# email: fernandofigaroli@gmail.com
# mi trovi su Google+
# Licenza: GPL 
"""
Inserire qui una descrizione generica di tutta la libreria MyOpen

class Gateway
    si connette al gateway in modalita normale o monitor
    invia e riceve comandi

class DB
    gestisce il database sqlite in cui tiene memorizzato il log
"""


class Gateway:
    """
    classe principale per la connessione al gateway
    
    """
    import sys

    ACK="*#*1##" #OK
    NACK="*#*0##" #ERROR
    MONITOR="*99*1##" 
    COMMAND="*99*0##" 

    def __init__(self,gateway,port,tipo=""):
        """definisco variabili principali per le connessioni al gateway
        se richiesto entro in modalita monitor"""
        self.gateway=gateway
        self.port=port
        self.tipoconnessione=tipo
        if tipo=="monitor":
            self.connect()

    def connect(self):
        """self.connect([tipo]) 
                effettua una connesione socket al gateway MyOpenWebNet
                uso: self.connect() - connessione normale per inviare comandi
        """             
        import socket
        try:
            self.Soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.Soc.connect((self.gateway,self.port))
        except:
            self.errore("Errore di connessione al gateway, verifica IP, porta e se accesso concesso senza password")
        
        if self.tipoconnessione=="monitor":
            self.Soc.send(self.MONITOR)
        else:
            self.Soc.send(self.COMMAND)
        #il gateway deve rispondere ACK ACK
        a1=self.readcmd() 
        a2=self.readcmd()
        if not a1==a2==self.ACK:
            self.errore("errore connessione... il gateway ha rispost: %s %s " % (a1,a2))
        return True 
        
    def close(self):
        """self.close()
                chiude la connessione socket al gateway se aperta
        """        
        if self.Soc: 
            self.Soc.close()
        return

    def sendcmd(self,cmd):
        """ self.send(str)
                invia il comando "str" al gateway e aspetta la risposta
                str deve contenere un codice OpenWebNet valido (es. *1*1*77##)
        """        
        R=True

        self.connect()
        try:
            self.Soc.send(cmd)
        except:    
            errore("Non stato possibile inviare il comando al gateway")

        #segnali di fine msg:
        #ACK =tutto bene, nulla da dire
        #NACK = segnale inviato, ma non andato a buon fine
        #risposta ACK = segnale inviato, risposta alla domanda, chiusura risposta
        mycmd=[]
        num_nack=0
        while True:
            R=self.readcmd()

            if R==self.ACK: 
                if mycmd==[]: mycmd=True
                self.close()
                return mycmd
            elif R==self.NACK:
                self.close()
                return False
            else:
                mycmd.append(R) 

    def readcmd(self):
        """ self.readcmd()
                legge dalla connessione socket una riga di messaggio
                per leggere piu testo metterlo in ciclo loop
        """
        #implementare errori
        #ricevo un carattere alla volta
        mycmd=""
        while True:
            try:
                R=self.Soc.recv(1)
            except:
                self.errore("non e stato possibile ricevere dal gateway")
            mycmd=mycmd+R
            #se fine comando "##" esco
            if mycmd[-2:]=="##":   
                return mycmd


    def errore(self,msg):
        self.close()
        self.sys.exit(msg) 


class Db:
    """
    Si occupa di gestire il database sqlite con memorizzato il logging dei comandi
    """
    import sqlite3

    def __init__(self,nomedb):
        """
        definisce le variabili generali del database e mi connetto
        """
        self.nomedb=nomedb
        self.connect=None

        try:
            self.connect=self.sqlite3.connect(self.nomedb)
        except self.sqlite3.Error, e:
            self.errore(e.args[0])

        #Verifico le tabelle presenti nel database
        cur = self.connect.cursor()
        cur.execute("SELECT name from sqlite_master WHERE type='table'")
        lista_tabelle=cur.fetchall()
        print "lista tabelle:"
        print lista_tabelle 

    
    def addrow(self, cmdopen, note):
        #oltre al cmdopen e eventuale note inserisco ID progressivo e TIME in secondi dal 1970
        pass

    def delrow(self, del_id):
        #cancello il record con del_id
        pass
    def readrow(self, read_id):
        #leggo una determinata riga
        pass
    def lastrow(self, CHI ):
        pass
            
    def close(self):
        if self.connect:
            self.connect.close()

    def errore(self,msg):
        self.close()
        self.sys.exit(msg) 


class Parser:
    """
    Fa il parsing dei codici my-open
    uso:
    pars=MyOpen.Parser(codice_open)
    pars --> object
    pars.who
    etc---    
    """
    import ConfigParser
    import re

    def __init__(self,lang="IT"):
        self.LANG=lang
       
        self.who=""
        self.who_human=""
        self.who_flag=False
        self.what=""
        self.what_human=""
        self.what_flag=False
        self.where=""
        self.where_human=""
        
        #load lists regex
        import regex
        self.regex={"0":regex.W0,"1":regex.W1}

    def __readHuman(self,fileconfig,section,key):
        fileconfig=self.LANG+"/"+fileconfig+".diz"
        try:
            config=self.ConfigParser.RawConfigParser()
            config.read(fileconfig)
            human=config.get(section, key)
        except:
            human="Not Found"
        return human

    def parsing(self,cod):
        self.COD=cod
        
        self.__who()
        self.__regex()
        
    def __who(self):
        self.who=self.COD.split('*')[1]

        if self.who[0]=="#":
            self.who=self.who[1:]
            self.who_flag=True
        
        #cercare who in archivio
        self.who_human=self.__readHuman("WHO","WHO",self.who)
        return 

    def __regex(self):
        #usando who vado a recuperare tutte le regex che lo riguardano
        #converto i * in X e tolgo gli ultimi due ##
        tempCOD=self.COD.replace("*","X").rstrip("##")
        #corrispondenza variabili
        dvar={"A":"WHAT","B":"WHERE"}
        for reg in self.regex[self.who]:
            pars=self.re.compile(reg[0])
            res=pars.match(tempCOD)
            if res:
                resdict=res.groupdict()
                print resdict
                for chiave in resdict.keys():
                    if chiave[-1]=="H":
                        resdict[chiave]=self.__readHuman(dvar[chiave[0]],self.who,resdict[chiave])
                    print resdict[chiave]
                print reg[1].format(**resdict)
                 
            break


    def __str_(self):
        #format output
        pass

