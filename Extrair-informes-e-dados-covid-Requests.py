#!/usr/bin/python
#SUBSTITUA python3 POR python SE ESTIVER NO WINDOWS
#########################################################################################################################################################################################################################
#Desenvolvido por: Lucas Coelho de Almeida
#
#Forma de uso: Funciona como um daemon, ou seja, execute a partir de uma tela de comando e deixe rodando indefinidamente
#
#Objetivo: Programa que a cada periodo de tempo, extrai relatorios da url designada e chama outro script que extrai dados desses
#          relatorios e os salva em formato de tabela .csv, e depois, chama um script que coloca esses dados em um banco para
#          serem servidos numa api. Arquivos de log em formato .csv sao gerados. Necessario manter esquema de pastas para
#          correto funcionamento.
#
#Esquema de pastas: Pasta ''Webscrapping-SESDF''
#                   |   
#                   ---->Script ''Extrair-dados-pdf.py'' que extrai dados em pdf para tabelas csv
#                   |
#                   ---->Script ''Extrair-informes-e-dados-covid-Requests.py'' que roda como daemon
#                   |
#                   ---->Arquivo ''log-extracao-dados.csv'' que eh criado e alimentado pelo script ''Extrair-dados-pdf.py''
#                   |
#                   ---->Arquivo ''log-extracao-web.csv'' que e criado eh alimentado pelo script ''Extrair-informes-e-dados-covid-Requests.py''
#                   |  
#                   |
#                   --->Pasta ''PROGRAMA-dados-extraidos-covid''
#                   |   |
#                   |   ---->Tabelas .csv com os dados extraidos sao mantidas aqui ate que sejam copiadas para o banco, depois sao excluidas
#                   |   ---->Script que salva os dados das tabelas no banco
#                   |
#                   --->Pasta ''PROGRAMA-backup-dados-extraidos-covid''
#                   |   |
#                   |   ---->Tabelas .csv com os dados extraidos sao copiadas aqui e mantidas indefinidamente
#                   |
#                   --->Pasta ''PROGRAMA-informes-covid''
#                   |   |
#                   |   ---->Relatorios em formato .pdf sao copiados aqui e mantidos indefinidamente
#                   |
#                   --->Pasta ''PROGRAMA-informes-download''
#                   |   |
#                   |   ---->Relatorios em formato .pdf baixados sao mantidos aqui temporariamente, e sempre no inicio ou fim de execucao de uma sessao, sao excluidos
#                   |
#                   --->Pasta ''PROGRAMA-localidades''
#                       |
#                       ---->Tabela em formato .csv com os nomes e coordenadas das localidades que serao buscadas na extracao. Essa lista funciona para filtragem e validacao
#
#Obs.: Esse script contem linhas comentadas que o habilitam a fazer a mesma extracao usando Selenium. Por hora nao se faz necessario,
#      pois a extracao eh simples e feita usando o pacote Requests. Porem, caso a pagina web passe a ter rotinas de javascript mais avanÃƒÂ§adas,
#      se torna necessario usar Selenium novamente. A preferencia pelo pacote Requests permanece pela maior velocidade e menor uso de recursos.
###########################################################################################################################################################################################

#Pacotes a serem usados e/ou importados#############################################
####################################################################################
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.firefox.options import Options
import requests
import wget
from bs4 import BeautifulSoup
import time
import os
#import codecs
import unicodedata
import csv
import datetime
import shutil
from pathlib import Path
import re
####################################################################################


#Variaveis globais necessarias######################################################
####################################################################################
link_sesdf='http://www.saude.df.gov.br/boletinsinformativos-divep-cieves/'
nome_arquivo_log='log-extracao-web.csv'
now = datetime.datetime.now()
direc_folders=str(Path.cwd()).replace("\\","/")+"/" 
folder_report_name='PROGRAMA-informes-covid' 
folder_download_name='PROGRAMA-informes-download'
script_extrator_dados='Extrair-dados-pdf.py'
sleep_time=18000 #18000 segundos sao 5 horas
####################################################################################


#Funcao que limpa strings retirando e/ou substituindo caracteres especiais##########
####################################################################################
def strip_accents(text): 

    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)
####################################################################################



#INICIO DO PROGRAMA PRINCIPAL#######################################################
####################################################################################

#Loop eterno o qual garante o funcionamento adequado como daemon. Ao final, uma funcao de sleep
#reduz consumo de memoria a quase zero, permitindo funcionamento em background sem problema de uso de recursos.

#while 1:
#Comente o if abaixo e descomente o while acim e o sleep ao final para ser um programa que roda em background
#Trocou-se pela execucaoo simples para integracao com agendamento do "crontab" do linux
if 1:
    print("\n\nINICIANDO NOVA SESSÃO\n")
    try:
    #if(1): #Descomente essa linha e comente as linhas try logo acima e todo o bloco except ao final do programa caso nao consiga encontrar de forma clara a fonte de uma excecao
        #criacao do arquivo de log, se necessario
        if not os.path.isfile(nome_arquivo_log):
            with open(nome_arquivo_log, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["DATE","QNTD DE LINKS","LINK","NOME DO ARQUIVO","SUCESSO-FRACASSO"])
                f.close()
        
        files_downloaded = os.listdir(str(direc_folders+folder_download_name)) # dir is your directory path
        for file in files_downloaded:
            os.remove(str(direc_folders+folder_download_name+str("/")+str(file)))

        #mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
        # To prevent download dialog
        #options = Options()
        #options.headless = True
        #profile = webdriver.FirefoxProfile()
        #profile.set_preference('browser.download.folderList', 2) # custom location
        #profile.set_preference('browser.download.manager.showWhenStarting', False)
        #profile.set_preference('browser.download.dir', direc_folders+folder_download_name)
        #profile.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
        #profile.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
        #profile.set_preference("pdfjs.disabled", True)
        #profile.set_preference("browser.download.panel.shown", False)
        #browser = webdriver.Firefox(options=options,firefox_profile=profile)
        #browser = webdriver.Firefox()
        #browser.get(link_sesdf)
        #assert 'Yahoo' in browser.title
        #elem = browser.find_element_by_name('textoBusca')  # Find the search box
        #elem.send_keys(pesquisador + Keys.RETURN)
        #time.sleep(10)
        #parentElement = browser.find_element_by_id("conteudo")
        #elementList = parentElement.find_elements_by_tag_name("p")
        #print(len(elementList)-2)
        #print(elementList[0].text)
        #print(elementList[1].text)
        #print(elementList[2].text)
        #print(elementList[3].text)
        #print(number_files)

        r=requests.get(link_sesdf)
        soup = BeautifulSoup(r.text, 'html.parser')  
        lista_elements=(soup.find("div", {"id":"conteudo"})).select('a')
        #use para debugar erros vindos da pagina html
        #for index in range(len(lista_elements)):
        #    print(lista_elements[(len(lista_elements)-1)-index].contents)
        #    print("\n")
        #exit()
        
        lista_num_informes_elements=[]
        for element,index_interno in zip(lista_elements,range(len(lista_elements))):
            if(str(element.contents).find("forme")==-1):
                lista_elements.pop(index_interno)
        for element in lista_elements:
            #resolvendo as inconsistencias existentes nos conteudos das divs
            aux_str= str(element.contents).replace('\\xa0', '')
            aux_str=re.search(r"forme.+\d+", aux_str, re.IGNORECASE)[0]
            aux_str=re.search(r"\d+", aux_str, re.IGNORECASE)[0]
            aux=aux_str
            lista_num_informes_elements.append( int( aux ) )
            #print(str("\n")+str(element.contents))
            #print(aux_str)
            #print( aux)   
        list_dir = sorted(os.listdir(direc_folders+folder_report_name))
        for name,index_interno in zip(list_dir,range(len(list_dir))):
            if not name.endswith(".pdf"):
                list_dir.pop(index_interno)
        if(len(list_dir)>0):
            number_last_file = int((sorted(list_dir)[-1]).replace(".pdf",""))
        else:
            number_last_file=0

        lista_num_dir=[]
        for name,index_interno in zip(list_dir,range(len(list_dir))):
                lista_num_dir.append(int((list_dir[index_interno]).replace(".pdf","")))
        
        #index=number_files
        lista_num_informes_elements.sort()
        #use para debugar erros no processamento do html
        #for index in range(len(lista_num_informes_elements)):
        #    print(lista_num_informes_elements[index])
        #    print(lista_elements[(len(lista_elements)-1)-index].contents)
        #    print("\n")
        #exit()
        for num,index_interno in zip(lista_num_informes_elements,range(len(lista_num_informes_elements))):
            print(num)
            if(num not in lista_num_dir):
                time.sleep(1)
                name_file=str(num)+str(".pdf")
                try:
                    print(lista_elements[(len(lista_elements)-1)-index_interno]['href'])
                    #print(str(date.today()))
                    wget.download(lista_elements[(len(lista_elements)-1)-index_interno]['href'],direc_folders+folder_download_name)
                    time.sleep(30)
                    files_downloaded = os.listdir(direc_folders+folder_download_name) # dir is your directory path
                    os.rename(str(direc_folders+folder_download_name+str("/")+files_downloaded[0]),str(direc_folders+folder_report_name+str("/")+str(name_file)) )
                    time.sleep(30)
                    print(name_file)
                    with open(nome_arquivo_log, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([str((now.strftime("%Y-%m-%d %H:%M:%S"))),len(lista_elements),lista_elements[(len(lista_elements)-1)-index_interno]['href'],name_file,"sucesso"])
                        f.close()
                    #chamada para execucao do script que extrai os dados de arquivos em formato .pdf para tabelas em formato .csv, a chamada precisa do nome do arquivo
                    #no linux eh python3, no windows eh apenas python
                    print(str("python3 ")+str(direc_folders+script_extrator_dados+" "+name_file))
                    os.system(str("python3 ")+str(direc_folders+script_extrator_dados+" "+name_file))
                except Exception as e:
                    print(e)
                    with open(nome_arquivo_log, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([str((now.strftime("%Y-%m-%d %H:%M:%S"))),len(lista_elements),lista_elements[index_interno]['href'] if (lista_elements[index_interno]['href']) else "nothing",name_file,"FRACASSO"])
                        f.close()
            else:
                continue


            #index+=1



            #Descomente o bloco abaixo caso queira limitar a execucao a uma dada quantidade de iteracoes
            #time.sleep(5)
            #if(index>=100000):
            #    break

            


    except Exception as e:
        print(e)
        with open(nome_arquivo_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([str((now.strftime("%Y-%m-%d %H:%M:%S"))),str(0),"nothing","nothing","FRACASSO FALHA GERAL"])
            f.close()

    #print("\n\nFIM DA SESSÃO, DORMINDO POR "+str(sleep_time)+" segundos")
    #time.sleep(sleep_time)
####################################################################################






