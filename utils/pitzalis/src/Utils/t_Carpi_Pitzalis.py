import random as rn

def verifica_numero(valore):
  """Verifica se il valore fornito è un numero (intero o float).

  Args:
    valore: Il valore da verificare.

  Returns:
    True se il valore è un numero, False altrimenti.
  """
  try:
    # Prova a convertire il valore in un intero
    int(valore)
    return True
  except ValueError:
    try:
      # Se la conversione in intero fallisce, prova con un float
      float(valore)
      return True
    except ValueError:
      # Se anche la conversione in float fallisce, non è un numero
      return False


def crea_chimica(nomefile,specie,membrana,membrana_new,food_membrana,cat_membrana):


    #creo l'elenco delle specie food
    elenco_food=[]
    for el in membrana:
      elenco_food+=[el["specie"]]
      
    f=open(nomefile,"w")

    # azzero tutti gli alfa
    for i in range(len(specie)):
      specie[i]["alfa"]=0.0
    for i in range(len(food_membrana)):
      food_membrana[i]["alfa"]=0.0

    # stampo le specie
    stampaF_specie(f,specie[0])
    
    for el in specie:
      if el["nome"] in elenco_food: 
        stampaF_specie(f,el)
       
    for el in food_membrana:
        stampaF_specie(f,el)  

    for i in range(1,len(specie)):
      if specie[i]["nome"] not in elenco_food: 
        stampaF_specie(f,specie[i])

    f.write("\n")

    #reazioni membrana
    for el in membrana:
        stampaF_membrana(f,el)
        
    #aggiungo reazioni membrana per il food del contenitore
    for el in membrana_new:
        stampaF_membrana(f,el)

    #aggiungo reazioni per crescita del contenitore
    
    for i in range(len(cat_membrana)):
      reag=[food_membrana[i]["nome"],cat_membrana[i]["nome"]]
      prod=[specie[0]["nome"],cat_membrana[i]["nome"]]
      #print(reag)
      #print(prod)
      elemento={"reagenti":reag,"prodotti":prod,"coeff":cat_membrana[i]["cdiff"]}
      stampaF_reazione(f,elemento)

    #aggiungo le reazioni interne      
    for el in reazioni:
        stampaF_reazione(f,el)
          
    f.close()

def leggi_file(nomefile):
    f=open(nomefile,"r")

    riga=f.readline()

    specie=[]
    membrana=[]
    reazioni=[]    
    while riga != "":
        if len(riga.split())>1:
            if verifica_numero(riga.split()[1]):
                # appartiene alla lista delle specie
                elemento={"nome":riga.split()[0],"quant":eval(riga.split()[1]),"alfa":eval(riga.split()[2])}
                specie+=[elemento]
            elif verifica_numero(riga.split()[0]):
                # reazioni di membrana
                #print(riga.split())
                elemento={"concExt":eval(riga.split()[0]),"specie":riga.split()[2],"diff":eval(riga.split()[4])}
                #print(elemento)
                membrana+=[elemento]
            else:
                # reazioni normali
                reagenti=(riga.split(">")[0]).split("+")
                for i in range(len(reagenti)):
                    reagenti[i]=reagenti[i].strip()
                prodotti=riga.split(">")[1]
                coeff=eval(prodotti.split(";")[-1])
                prodotti=riga.split(">")[1].split(";")[0]
                prodotti=prodotti.split("+")
                for i in range(len(prodotti)):
                    prodotti[i]=prodotti[i].strip()
                elemento={"reagenti":reagenti[:],"prodotti":prodotti[:],"coeff":coeff}                     
                reazioni+=[elemento]
                
        riga=f.readline()

    return (specie,membrana,reazioni)

    for el in specie:
        stampaV_specie(el)
    for el in membrana:
        stampaV_membrana(el)        
    for el in reazioni:
        stampaV_reazione(el) 
            
def stampaV_specie(sp):
    print("%s\t%s\t%s"%(sp["nome"],str(sp["quant"]),str(sp["alfa"])))

def stampaF_specie(f,sp):
    f.write(sp["nome"]+"\t"+str(sp["quant"])+"\t"+str(sp["alfa"])+"\n")
    
def stampaV_membrana(sp):
    print("%s\t>\t%s\t>\t;\t%s"%(str(sp["concExt"]),sp["specie"],str(sp["diff"])))

def stampaF_membrana(f,sp):
    f.write(str(sp["concExt"])+"\t>\t"+sp["specie"]+"\t;\t"+str(sp["diff"])+"\n")

def stampaV_reazione(reaz):
    for i in range(len(reaz["reagenti"])-1):
        print("%s\t+\t"%(reaz["reagenti"][i]),end="")
    print("%s\t>\t"%(reaz["reagenti"][-1]),end="")   
    for i in range(len(reaz["prodotti"])-1):
        print("%s\t+\t"%(reaz["prodotti"][i]),end="")
    print("%s\t;\t"%(reaz["prodotti"][-1]),end="")
    print(reaz["coeff"])    

def stampaF_reazione(f,rz):
    #print(rz)
    #print(rz["reagenti"])
    #print(rz["prodotti"])
    
    for i in range(len(rz["reagenti"])-1):
        f.write(rz["reagenti"][i]+"\t+\t")       
    f.write(rz["reagenti"][-1]+"\t>\t")
    for i in range(len(rz["prodotti"])-1):
        f.write(rz["prodotti"][i]+"\t+\t")
    f.write(rz["prodotti"][-1]+"\t;\t")
    f.write(str(rz["coeff"])+"\n")    


def leggi_parametri(nomefile):
    f=open(nomefile,"r")

    nome_file=f.readline().split()[0]
    nome_file_out=f.readline().split()[0]

    quant_ini=eval(f.readline().split()[0])
    conc_ext=eval(f.readline().split()[0])
    m_diff=eval(f.readline().split()[0])
    Fr_sp_int=eval(f.readline().split()[0])
    Fr_catMem=eval(f.readline().split()[0])
    Cibo_catMem=eval(f.readline().split()[0])
    
    """
    nome_file=f.readline().split()[0].split(".")[0]
    nome_file_out=nome_file+"_out"
    nome_file+=".txt"
    nome_file_out+=".txt"
    """

    f.close()

    return (nome_file,nome_file_out,quant_ini,conc_ext,m_diff,Fr_sp_int,Fr_catMem,Cibo_catMem)


def leggi_file_modifiche():
    f=open("sp_cat_membrana.txt","r")

    riga=f.readline()
    riga=f.readline()
    
    r_membrana=[]
    food_membrana=[]
    cat_membrana=[]
    while riga != "":
        if len(riga.split())>1:
          #print(riga.split())
          elemento={"concExt":eval(riga.split()[2]),"specie":riga.split()[0],"diff":eval(riga.split()[3])}
          r_membrana+=[elemento]
          elemento={"nome":riga.split()[0],"quant":eval(riga.split()[1]),"alfa":0.0}
          food_membrana+=[elemento]
          elemento={"nome":riga.split()[4],"cdiff":eval(riga.split()[5])}
          cat_membrana+=[elemento]          
        riga=f.readline()
    f.close()

    """
    f=open("sp_food.txt","r")    
    riga=f.readline()

    elenco_food=[]    
    while riga != "":
      elenco_food+=[riga.split()[0]]      
      riga=f.readline()
    f.close()
    """

    return (r_membrana,food_membrana,cat_membrana)


#(file_orig,file_out,quant_ini,conc_ext,m_diff,Fr_sp_int,Fr_catMem,Cibo_catMem)=leggi_parametri("parametri_tCP.txt")

(specie,membrana,reazioni)=leggi_file("chimica_in.txt")
(membrana_new,food_membrana,cat_membrana)=leggi_file_modifiche()
crea_chimica("chimica.txt",specie,membrana,membrana_new,food_membrana,cat_membrana)


