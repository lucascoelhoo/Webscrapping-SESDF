cd /home/simop/webscrapping-sesdf/Webscrapping-SESDF/PROGRAMA-dados-extraidos-covid

mkdir output

for f in *.csv; do awk -v d="$f" -F"," 'BEGIN {OFS = ","} FNR==1{$(NF+1)="dataExtracao"} FNR>1{$(NF+1)=d;} 1' RS="\r\n" $f > output/$f; done

cd output

for f in *.csv; do docker cp $f MONGODB_BSB_DATA_COVID:/tmp/; docker exec MONGODB_BSB_DATA_COVID mongoimport --type csv -d bsbdatacovid -c regions --headerline --file /tmp/$f; done

rm /home/simop/webscrapping-sesdf/Webscrapping-SESDF/PROGRAMA-dados-extraidos-covid/output/*.csv
