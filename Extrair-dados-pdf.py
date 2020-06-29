#!/usr/bin/python
#########################################################################################################################################################################################################################
#Desenvolvido por: Lucas Coelho de Almeida
#
#Forma de uso: Execute a partir de uma tela de comando passando o nome do arquivo
#              como argumento (incluir o ".pdf'"). Para rodar para todos os arquivos na pasta ''PROGRAMA-informes-covid'', execute com "*.pdf"
#
#Objetivo: Extrator de dados de relatorios em formato .pdf para tabelas em formato .csv . Busca, usando expressoes regulares, por tabela especifica
#          presente no relatorio da secretaria de saude de DF. Necessario manter esquema de pastas para correto funcionamento.          
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
#Obs.: Ao fim da execucao, copia o arquivo .csv criado para a pasta ''PROGRAMA-dados-extraidos-covid'' e chama script que passa esses dados para um
#      banco de dados. Ao fim dessa execucao, exclui o arquivo dessa pasta. Assim, a aplicacao consegue trabalhar com qualquer esquema de armazenamento de dados.
###########################################################################################################################################################################################

#Pacotes a serem usados e/ou importados#############################################
####################################################################################
import csv
import glob
import os
import re
import sys
import pandas as pd
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import datetime
#pd.options.display.mpl_style = 'default'
import sys
import tika
from tika import parser
tika.initVM()
import unicodedata
import shutil
import time
from pathlib import Path
####################################################################################


#Variaveis globais necessarias######################################################
####################################################################################
filename_entry=sys.argv[1]
#filename_entry="*.pdf" #Pode-se descomentar essa linha e comentar a anterior para rodar o programa sem a necessidade de chamada externa
print(filename_entry)

excluir_essa_linha="RA em investigaÃ§Ã£o" #Linha que, em alguns caso, apresentou problemas de formatacao e nao tem valor para pesquisa, e portanto, caso necessario, eh excluida da extracao

input_path = str(Path.cwd())+"/" #Como estamos usando relative paths, nÃ£o precisamos do caminho, mas caso precisemos, basta alterar essa variavel, lembrando ser necessÃ¡rio usar / como divisor

reports_directory="PROGRAMA-informes-covid"

csv_directory="PROGRAMA-dados-extraidos-covid"

csv_backup_directory="PROGRAMA-backup-dados-extraidos-covid"

localidades_directory="PROGRAMA-localidades"

localidades_file="localidades.csv"

nome_arquivo_log="log-extracao-dados.csv"
now = datetime.datetime.now()

#Mude a variavel abaixo para true e coloque o nome do script que for usado. O script
#deve ser posto na pasta "PROGRAMA-dados-extraidos-covid" e deve ser capaz de salvar
#no banco de destino todos os arquivos em formato .csv quando for chamado. Apos
#a chamada, todos os arquivos em formato .csv sao excluidos dessa pasta.
Chama_script_banco_dados=True
nome_script_banco_dados="import_data.sh"
####################################################################################



#Funcao que limpa strings retirando e/ou substituindo caracteres especiais###########################
#####################################################################################################
def strip_accents(text):

    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)
#####################################################################################################


#Funcao que busca e extrai os dados do relatorio, gerando o frame de dados do pacote pandas##########
#####################################################################################################
def create_df(pdf_content, content_pattern, line_pattern, column_headings,primeira_palavra_linha_tabela):
    """Create a Pandas DataFrame from lines of text in a PDF.

    Arguments:
    pdf_content -- all of the text Tika parses from the PDF
    content_pattern -- a pattern that identifies the set of lines
    that will become rows in the DataFrame
    line_pattern -- a pattern that separates the agency name or revenue source
    from the dollar values in the line
    column_headings -- the list of column headings for the DataFrame
    """
    try:
    #if 1:
        list_of_line_items = []
        #print(re.search(content_pattern, pdf_content, re.DOTALL))
        # Grab all of the lines of text that match the pattern in content_pattern
        content_match = re.search(content_pattern, pdf_content, re.DOTALL)
        #try:
        #    content_match=content_match[0]
        #except:{}
        # group(1): only keep the lines between the parentheses in the pattern
        content_match = content_match.group(1)
        
        #print(content_match)
        # Split on newlines to create a sequence of strings
        content_match = content_match.split('\n')
        #print(content_match)
        # Iterate over each line
        content_match=content_match[:-1]
        flag_terminou_pular_linhas=False

        for item in content_match:
            if (not(re.search(primeira_palavra_linha_tabela, item, re.I)) and (flag_terminou_pular_linhas==False)):
                continue
            else:
                flag_terminou_pular_linhas=True
            # Create a list to hold the values in the line we want to retain
            line_items = []
            # Use line_pattern to separate the agency name or revenue source
            # from the dollar values in the line
            try:
                #print(re.search(r'^.*?(\d)', item, re.I))
                line_match = re.search(line_pattern, item, re.I)
                #print(str(line_match.group(0))[:-2])
                #quit()
                # Grab the agency name or revenue source, strip whitespace, and remove commas
                # group(1): the value inside the first set of parentheses in line_pattern
                agency=""
                agency = str(line_match.group(0))[:-2]
                agency=(strip_accents(str(agency).replace(" ","")).lower().replace("*",""))
                #print(agency)
                latitude=""
                longitude=""
                localidade_deu_certo=False
                for localidades_interno,latitudes_interno,longitudes_interno,nome_oficial_interno in zip(lista_geral_localidades,lista_geral_latitudes,lista_geral_longitudes,lista_geral_localidades_nome_oficial):
                    if((strip_accents(str(agency)).lower()) == localidades_interno):
                        latitude=latitudes_interno
                        longitude=longitudes_interno
                        agency=nome_oficial_interno
                        localidade_deu_certo=True
                        break
                if(localidade_deu_certo==False):
                    continue
                        
                

                

                #agency=agency.replace("*","")
                # Grab the dollar values, strip whitespace, replace dashes with 0.0, and remove $s and commas
                # group(2): the value inside the second set of parentheses in line_pattern
                #print(str(item))
                values_string = str(item).replace(str(line_match.group(0))[:-2],"").replace(",",".")

                #print(values_string)
                values_string_aux=values_string.split()
                for string_interno,ind_interno in zip(values_string_aux,range(len(values_string_aux))):
                    if not((string_interno.replace(".","")).isnumeric()):
                        print(string_interno)
                        values_string_aux.pop(ind_interno)    
                values_string=" ".join(values_string_aux)
                
                values_string=values_string.split(" ")
                #print(values_string)
                for cel,ind in zip(values_string,range(len(values_string))):
                    if not(cel.replace(".","").isnumeric()):
                        
                        #print(cel)
                        values_string.pop(ind)

                for cel,ind in zip(values_string,range(len(values_string))):
                    if not(cel.find(".")==-1):
                        if(len(cel.split(".")[1])>=3):
                            #print(cel)
                            #print(cel.split(".")[1])
                            values_string[ind]=str(cel.split(".")[0])+str(cel.split(".")[1])  
                            print(values_string[ind])
                            print(values_string)
                            print(" ")
                # Split on whitespace and convert to float to create a sequence of floating-point numbers
                values = values_string
                #print(values_string)
                #print("FOI ATE AQUI")
                for valor,cont_valor in zip(values,range(len(values))):
                    if not (str(valor).replace(".","").isnumeric()):
                        values[cont_valor]=int(0)
                #print(values)
                # Extend the floating-point numbers into line_items so line_items remains one list
                # Append the agency name or revenue source into line_items
                line_items.append(str(agency))
                line_items.append(str(latitude))
                line_items.append(str(longitude))                
                # Append line_item's values into list_of_line_items to generate a list of lists;
                line_items.extend(values)
                if(len(line_items)<=6):
                    line_items.append(int(0))
                    line_items.append(int(0))
                # all of the lines that will become rows in the DataFrame
                list_of_line_items.append(line_items)
            except Exception as e:#{}
                print(e)
        #for line in list_of_line_items:
        #    print(len(line))
        #    print(line)
         #Convert the list of lists into a Pandas DataFrame and specify the column headings
        df = pd.DataFrame(list_of_line_items, columns=column_headings)
        return df
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
#####################################################################################################


#Funcao que faz plotagem dos frames de dados do pacote pandas, nao eh usada mas esta disponivel######
#####################################################################################################
def create_plot(df, column_to_sort, x_val, y_val, type_of_plot, plot_size, the_title):
    """Create a plot from data in a Pandas DataFrame.

    Arguments:
    df -- A Pandas DataFrame
    column_to_sort -- The column of values to sort
    x_val -- The variable displayed on the x-axis
    y_val -- The variable displayed on the y-axis
    type_of_plot -- A string that specifies the type of plot to create
    plot_size -- A list of 2 numbers that specifies the plot's size
    the_title -- A string to serve as the plot's title
    """
    # Create a figure and an axis for the plot
    fig, ax = plt.subplots()
    # Sort the values in the column_to_sort column in the DataFrame
    df = df.sort_values(by=column_to_sort)
    # Create a plot with x_val on the x-axis and y_val on the y-axis
    # type_of_plot specifies the type of plot to create, plot_size
    # specifies the size of the plot, and the_title specifies the title
    df.plot(ax=ax, x=x_val, y=y_val, kind=type_of_plot, figsize=plot_size, title=the_title)
    # Adjust the plot's parameters so everything fits in the figure area
    plt.tight_layout()
    # Create a PNG filename based on the plot's title, replace spaces with underscores
    pngfile = the_title.replace(' ', '_') + '.png'
    # Save the plot in the current folder
    plt.savefig(pngfile)
#####################################################################################################


#INICIO DO PROGRAMA PRINCIPAL########################################################################
#####################################################################################################

#Primeiramente, sao carregadas as localidades e respectivas coordenadas 
lista_preliminar_localidades = pd.read_csv(localidades_directory+"//"+localidades_file)
lista_geral_localidades=[]
lista_geral_localidades_nome_oficial=[]
lista_geral_latitudes=[]
lista_geral_longitudes=[]
for localidades_interno,latitudes_interno,longitudes_interno,nome_oficial_interno in zip(lista_preliminar_localidades['regiao'],lista_preliminar_localidades['latitude'],lista_preliminar_localidades['longitude'],lista_preliminar_localidades['nome oficial']):
    lista_geral_localidades.append(strip_accents(str(localidades_interno)).lower())
    lista_geral_latitudes.append(str(latitudes_interno))
    lista_geral_longitudes.append(str(longitudes_interno))
    lista_geral_localidades_nome_oficial.append(str(nome_oficial_interno))


#criacao do arquivo de log, se necessario
if not(os.path.isfile(nome_arquivo_log)):
    with open(nome_arquivo_log, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["DATE","NUMERO/NOME DO RELATORIO","SUCESSO-FRACASSO"])
        f.close()
        
#Expressoes regulares que serao usadas na busca dos dados
expenditures_pattern = r'REGIÃƒO/RA(.*)(?i:total df)' #Buscar por tudo entre as duas expressoes, ignorando maisuculas e minusculas no segundo termo
expenditures_pattern2 = r'REGIÃƒO/RA(.*)TOTAL DF' #Buscar por tudo entre as duas expressoes
covid_pattern = r'^.*?(\d)' #Estrutura dos dados de cada linha da tabela

#Nome verificado na primeira linha relevante da tabela, eh necessario para tentar evitar ao maximo quaisquer erros de formatacao da SES-DF
primeira_palavra_linha_tabela="Sudoeste"

# Nomes das colunas verificadas na tabela a ser extraida
covid_columns_8args = ['regiao', 'latitude','longitude', 'num', 'porcentagem', 'incidencia','obitos','porcentagem obitos']
covid_columns_6args = ['regiao', 'latitude','longitude', 'num', 'porcentagem', 'incidencia']

#O bloco abaixo verifica se a chamada do programa ira ser executada para varios relatorios e, caso afirmativo, exclui quaisquer tabelas ja existentes na pasta alvo
if(filename_entry=="*.pdf"):
    try:
        list_files_csv=glob.glob(os.path.join(input_path+csv_directory, '*.csv'))
        # Iterate over all csv files in the folder and process each one in turn
        for input_file in zip(list_files_csv):
            os.remove(input_path+csv_directory+input_file)
    except:{}


# Iterate over all PDF files in the folder and process each one in turn
for input_file in glob.glob(os.path.join(input_path+reports_directory, filename_entry)):
        try:
        #if 1:
            # Nome do arquivo pdf
            filename = os.path.basename(input_file)
            print(filename)
            # Remove o .pdf do nome, caso va ser usado no plot
            plotname = filename.strip('.pdf')

            # Tika eh usado para fazer o parse dos dados do arquivo
            parsedPDF = parser.from_file(input_file)
            # Conteudo geral do arquivo eh extraido
            pdf = parsedPDF["content"]
            
            # Pulos de linhas duplicados sao excluidas
            pdf = pdf.replace('\n\n', '\n')
            pdf = pdf.replace('  ', ' ')
            pdf = pdf.replace('  ', ' ')
            #Data do relatorio eh extraida
            date_string=str(pdf)[str(pdf).find("Boletim EpidemiolÃ³gico do dia ")+len("Boletim EpidemiolÃ³gico do dia "):str(pdf).find("Boletim EpidemiolÃ³gico do dia ")+len("Boletim EpidemiolÃ³gico do dia ")+10]
            date=date_string.split(".")
            #print(date[0])
            #print(date[1])
            #print(date[2])
            #print(pdf)

            
            #Sequencia de tentativas de extracao usando a funcao "create_df". Existem relatorios com tabelas de tamanhos diferentes, pois
            #o numero de mortes e outros dados nao estavam presentes anteriormente, mas isso nao pode impedir a normalizacao dos dados 
            #no banco, entao essa sequencia tenta garantir que todas as tabelas .csv geradas sejam o maximo possivel iguais.
            try:
                try:
                    covid_df = create_df(pdf, expenditures_pattern, covid_pattern, covid_columns_8args,primeira_palavra_linha_tabela)
                except:
                    covid_df = create_df(pdf, expenditures_pattern, covid_pattern, covid_columns_6args,primeira_palavra_linha_tabela)
            except:
                try:
                    covid_df = create_df(pdf, expenditures_pattern2, covid_pattern, covid_columns_8args,primeira_palavra_linha_tabela)
                except:
                    covid_df = create_df(pdf, expenditures_pattern2, covid_pattern, covid_columns_6args,primeira_palavra_linha_tabela)

            #print(covid_df)
            # print(revenue_df)

            # Uso da funcao de plotagem
            #create_plot(covid_df, "regiao", "regiao", "num", 'barh', [20,10], plotname+"Dados-Covid")
            
            try:
            #if 1: #Descomente essa linha e comente as linhas try logo acima e todo o bloco except correspondente caso nao consiga encontrar de forma clara a fonte de uma excecao

                #o comando abaixo eh o responsavel por criar o arquivo csv exportando o frame do pacote pandas. A variavel ''plotname'' tem o mesmo nome do arquivo
                #de destino, por isso foi reutilizado em todo o programa. Inicialmente, a intencao era que o programa salvasse os plots.
                covid_df.to_csv(input_path+csv_backup_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')

                if(Chama_script_banco_dados==True):
                    covid_df.to_csv(input_path+csv_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')
                    os.system(str("cd ")+str(input_path)+csv_directory+str(" && ")+str(input_path+csv_directory+"/"+nome_script_banco_dados))
                    time.sleep(5)
                    os.remove(input_path+csv_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')
                
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Warning:")
                print(exc_type, fname, exc_tb.tb_lineno)
                pdf = pdf.replace('\n\n', '\n')
                datas_encontradas=re.search("(\d)(\d)/(\d)(\d)/(\d)(\d)(\d)(\d)", pdf, re.DOTALL)
                date_string=str(datas_encontradas.group(0))
                date=date_string.split("/")
                print(date)
                covid_df.to_csv(input_path+csv_backup_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')
                if(Chama_script_banco_dados==True):
                    covid_df.to_csv(input_path+csv_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')
                    os.system(str(input_path+csv_directory+"/"+nome_script_banco_dados))
                    time.sleep(5)
                    os.remove(input_path+csv_directory+"/"+plotname+"_"+date[2]+"-"+date[1]+"-"+date[0]+'.csv')

            with open(nome_arquivo_log, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([(now.strftime("%Y-%m-%d %H:%M:%S")),plotname,"sucesso"])
                print("SUCESSO: "+str(plotname) )
                f.close()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            with open(nome_arquivo_log, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([(now.strftime("%Y-%m-%d %H:%M:%S")),plotname,"FRACASSO"])
                print("FRACASSO: "+str(plotname) )
                f.close()

#####################################################################################################



