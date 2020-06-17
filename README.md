# Webscrapping-SESDF

- Desenvolvido por: Lucas Coelho de Almeida

- Objetivo: Suíte de programas em linguagem Python que a cada período de tempo, extrai relatorios da url designada (http://www.saude.df.gov.br/boletinsinformativos-divep-cieves/) e chama outro script que extrai dados desses relatorios e os salva em formato de tabela .csv, e depois, pode ou não chamar um script que coloca esses dados em um banco para serem servidos numa api.  Ao fim, a aplicação mantém os informes em formato ".pdf" salvos, as tabelas em formato ".csv" e arquivos de log com indicações do funcionamento das últimas tentativas. A tabela de interesse a ser extraída é a que relaciona informações por grandes regiões e regiões administrativas do DF.
 
- Forma de uso: É um script que roda apenas uma vez e deve ter sua chamada agendada usando o serviço "crontab". Anteriormente era um daemon por si só, mas a solução de agendamento é bem mais adequada. Idealmente, também deveria-se configurar um servidor de email (ou um smtp relay) e configurar envios de email pelo "crontab" também. É possível descomentar alguma linhas e voltar o script para o modelo de funcionamento em formato de daemon.

- Esquema principal de pastas da aplicação:
    - Webscrapping-SESDF
       - Script ''Extrair-dados-pdf.py'' que extrai dados em pdf para tabelas csv
       - Script ''Extrair-informes-e-dados-covid-Requests.py'' que roda como daemon
       - Script ''crontab-py.py'' que agenda a chamada do script ''Extrair-informes-e-dados-covid-Requests.py'' a cada 2 horas
       - Arquivo ''log-extracao-dados.csv'' que eh criado e alimentado pelo script ''Extrair-dados-pdf.py''
       - Arquivo ''log-extracao-web.csv'' que e criado eh alimentado pelo script ''Extrair-informes-e-dados-covid-Requests.py''
       - Pasta ''PROGRAMA-dados-extraidos-covid''
          - Tabelas .csv com os dados extraidos sao mantidas aqui ate que sejam copiadas para o banco, depois sao excluidas;
          - Script que salva os dados das tabelas no banco.
       - Pasta ''PROGRAMA-backup-dados-extraidos-covid''
          - Tabelas .csv com os dados extraidos sao copiadas aqui e mantidas indefinidamente.
       - Pasta ''PROGRAMA-informes-covid''
          -  Relatorios em formato .pdf sao copiados aqui e mantidos indefinidamente.
       - Pasta ''PROGRAMA-informes-download''
          - Relatorios em formato .pdf baixados sao mantidos aqui temporariamente, e sempre no inicio ou fim de execucao de uma sessao, sao excluidos.
       - Pasta ''PROGRAMA-localidades''
          - Tabela em formato .csv com os nomes e coordenadas das localidades que serao buscadas na extracao. Essa lista funciona para filtragem e validacao.


- Observações adicionais: 
    - O funcionamento da aplicação segue o seguinte fluxo:
        - Programa "Extrair-informes-e-dados-covid-Requests.py" é chamado pelo daemon nativo do Linux "cron" através do agendamento feito no "crontab"
        - Na nova sessão, lista os links disponíveis para download no link provido pela SESDF, compara a quantidade desses com a quantidade de arquivos presentes na pasta "PROGRAMA-informes-covid" e, caso existam mais links que arquivos, baixa os mais novos de forma provisória na pasta "PROGRAMA-informes-download". Importante observar que não existe verificação de nome dos arquivos nem dos links usados, somente pela quantidade. O arquivo de log "log-extracao-web.csv" contém a data e horário da sessão, a quantidade de links que existia no momento da requisição na página, o link usado para download de cada arquivo e o status de sucesso ou fracasso, ou ainda fracasso geral do aplicaçao de download.
        - Para cada informe baixado, o script "Extrair-dados-pdf.py" é chamado, o qual extrai os dados e os salva de forma estruturada em arquivos com extensão ".csv" na pasta "PROGRAMA-backup-dados-extraidos-covid". Este pode, de forma opcional, executar um script que leia e salve os dados de todos os arquivos ".csv" presentes na pasta "PROGRAMA-dados-extraidos-covid", devendo este programa externo estar presente nessa mesma pasta e ser indicado no bloco indicado no código desse script (existem duas variáveis para tal fim).
        - O programa encerra a sessão e sai, sendo necessária nova chamada. O arquivo de log "log-extracao-dados.csv" contém a data e horário da tentativa de extração, o nome do arquivo em formato ".pdf" o qual era o alvo da extração e o status de sucesso ou fracasso da extração.
    - É necessario manter esquema de pastas inalterado para correto funcionamento.
    - Os arquivos de log existentes no repositório são apenas exemplos, devendo ser excluídos em caso de reuso do projeto.
    - Os informes em formato ".pdf" e as tabelas em formato ".csv" presentes nas pastas "PROGRAMA-backup-dados-extraidos-covid" e "PROGRAMA-informes-covid" são oficiais e representam o resultado das extrações da aplicação até o dia 27/05/2020. Caso deseje repetir toda a extração, exclua esses arquivos dessas pastas e certifique-se que todas as pastas, exceto a "PROGRAMA-localidades" estejam vazias.
    - A pasta "PROGRAMA-localidades" contém um arquivo em formato ".csv" que relaciona as localidades e coordenadas geográficas de cada região administrativa e conjunto de regiões existentes na tabela de interesse dos informes diculgados pela SESDF.
    - Os informes só passaram a ter a tabela de interesse a partir do dia 26/03/2020.
    - Mudanças muito drásticas na formatação do documento ou da tabela demandarão revisões do código, embora grande parte das irregularidades presentes nos informes divulgados até o dia 27/05/2020 já foram solucionados.
    -É necessário se atentar à questão de permissionamento nas pastas e nos scripts quando usado em Linux, tudo nas subpastas deve estar liberado para não ocorrerem erros indesejados que não terão relação com o programa em si.
    -Problemas e inconsistências em caminhos ocorrem quando se usa "\\" do Windows no Linux. Troque por "/" e prefira o uso da biblioteca "path", dos métodos "join" e semelhantes.
    -Para evitar erros indesejados rodando em Linux, não esqueça da importância da linha shebang (). 
    -No Windows, relative paths funcionam muito bem, no Linux não, portanto, para ficar universal, prefira usar o método "Path.cwd()" da "pathlib" para sempre obter o diretório do script/projeto rodando.
