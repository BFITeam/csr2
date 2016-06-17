import boto.mturk.connection
from apscheduler.schedulers.blocking import BlockingScheduler
import website.wsgi
from django.contrib.auth.models import User
import os

sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
real_host = 'mechanicalturk.amazonaws.com'


mturk = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    host = real_host,
    debug=1
)

hitid = '3TRB893CSJVXBXOSIRQD01OSYEYG7T'
responses = []
for assignment in mturk.get_assignments(hitid):
    answers = assignment.answers[0]
    for a in answers:
        if a.qid == "Age":
            responses.append(a.fields[0])


print responses
#assignments = [a.answers[0][0].fields[0] for a in mturk.get_assignments('3TRB893CSJVXBXOSIRQD01OSYEYG7T')]
#print assignments
scheduler = BlockingScheduler()

#mturk.create_hit(hit_layout='3EC4IFE3XHELSEQ9RHPWH6DCRJ40V7', max_assignments=1, reward=.06)
def main():
    #GET ALL THE HITS. THEN TRY TO GET USER OBJECT
    #IF ERROR, SEND MESSAGE THAT KEY WAS INCORRET
    #IF CORRECT, SEND MESSAGE THE KEY HAS BEEN VERIFIED
    #AND ACTIVATED
    pass


#scheduler.add_job(main, 'interval', minutes=1)
