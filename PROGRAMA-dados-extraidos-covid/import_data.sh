cd /home/simop/webscrapping-sesdf/Webscrapping-SESDF/PROGRAMA-dados-extraidos-covid

for f in *.csv; do docker cp $f MONGODB_BSB_DATA_COVID:/tmp/; docker exec MONGODB_BSB_DATA_COVID mongoimport --type csv -d bsbdatacovid -c regions --headerline --file /tmp/$f; done
