import pandas
import glob
import os
import csv, sqlite3
from pathlib import Path
import sys
db_path="/home/simop/api-dados-extraidos-sesdf"
db_name="dados-extraidos-covid19-sesdf.db"
table_name='dados-extraidos-covid19-sesdf'
print("Script SQLite")
conn = sqlite3.connect(os.path.join(db_path, db_name)) # change to 'sqlite:///your_filename.db'
csvfiles_path=str(Path.cwd())
filename_entry=sys.argv[1]
#filename_entry="*.csv"

for input_file in glob.glob(os.path.join(csvfiles_path, filename_entry)):
    df = pandas.read_csv(input_file, index_col=0)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    print(input_file)


