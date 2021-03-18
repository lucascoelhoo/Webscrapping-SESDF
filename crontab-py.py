from crontab import CronTab
from pathlib import Path

filename='Extrair-informes-e-dados-covid-Requests.py'
cron = CronTab(user=True)
job = cron.new(command=str(str("cd ")+ str(Path.cwd())+str(" && ")+str('/usr/bin/python3 '+ str(Path.cwd())+'/'+filename)))
job.minute.every(120)

cron.write()
