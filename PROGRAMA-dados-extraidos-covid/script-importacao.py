import pandas
import glob
import os
import csv, sqlite3
from pathlib import Path
import sys
import sqlite3



#db_path="/home/simop/api-dados-extraidos-sesdf"
db_path="C:/Users/lucas/Desktop/UNB/Mestrado/Projetos/App-Covid-19/api-dados-extraidos-sesdf"
db_name="dados-extraidos-covid19-sesdf.db"
table_name='dados-extraidos-covid19-sesdf'
print("Script SQLite")
conn = sqlite3.connect(os.path.join(db_path, db_name)) # change to 'sqlite:///your_filename.db'
csvfiles_path=str(Path.cwd())
#filename_entry=sys.argv[1]
filename_entry="37.csv"
for input_file in glob.glob(os.path.join(csvfiles_path, filename_entry)):
    df = pandas.read_csv(input_file, index_col=0)
    for index,row in df.iterrows():
        conn = sqlite3.connect(db_path+"/"+db_name)
        with conn:
            sqlQuery    = "select * from `"+table_name+"` where dataExtracao=\"%s\" and regiao=\"%s\";"
            cursorObject = conn.cursor()
            cursorObject.execute(sqlQuery % (str(row['dataExtracao']),str(row['regiao'])))
            rows = cursorObject.fetchall()
            if not rows:
                sqlQuery    = "INSERT INTO `"+table_name+'''` (dataExtracao,regiao,latitude,longitude,num,porcentagem,incidencia,obitos,`porcentagem obitos`) 
                                VALUES(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")'''
                cursorObject.execute(sqlQuery % (str(row['dataExtracao']),str(row['regiao']),str(row['latitude']),str(row['longitude']),str(row['num']),str(row['porcentagem']),str(row['incidencia']),str(row['obitos']),str(row['porcentagem obitos'])))
                rows = cursorObject.fetchone()
                print(rows)
            else:
                print("Linha repetida, não irei adicionar!")
        conn.close()
    print(input_file)


