import boto
from apscheduler.schedulers.blocking import BlockingScheduler
import website.wsgi
from django.contrib.auth.models import User

mturk = boto.connect_mturk()
scheduler = BlockingScheduler()

def main():
    #GET ALL THE HITS. THEN TRY TO GET USER OBJECT
    #IF ERROR, SEND MESSAGE THAT KEY WAS INCORRET
    #IF CORRECT, SEND MESSAGE THE KEY HAS BEEN VERIFIED
    #AND ACTIVATED


scheduler.add_job(main, 'interval', minutes=1)
