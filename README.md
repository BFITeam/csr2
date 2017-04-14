# csr

Online protal for employee data entry tasks


### Set up
This a Django project using Python 2.7.  I recommend installing requirements to your local machine in a virtual environment.

You'll need to employ some service(Hopefully Heroku is still a thing) to serve your app on the WORLD WIDE WEB.  Assuming a Heroku deploy you'll need to set the following environmental variables, locally and on your Heroku application.

1. admin_email
2. admin_password
3. AWS_ACCESS_KEY_ID  You need to retrieve this and the next from Amazon's developer tools.
4. AWS_SECRETE_ACCESS_KEY 
5. DATABASE_URL This is the url that heroku will asign when you allocate an database.  It will be set by heroku, so you only need to set this locally.
6. MYAPP_DEBUG set this to 0 on heroku but 1 if working locally.
7. SECRET_KEY this is your django projects secret key.  google for more info.

#### Some things to consider re: Heroku
The database you allocate to the app should be standard tier and you'll probably want to use professional web dynos.  Make sure to allocate a dyno for the worker.

### Treatments

There is a table in the database that has a list of the all the different assigments an individual might recieve.  There is a file called treatmentcells.csv that you can look at for reference.  If you want 100 subjects, then the treatmentcells.csv should have 100 rows.  Format this file exactly as the example appears.  

IMPORTANT: There is a column called "batch" in the treatmentcells.csv.  Choose some unique name everytime you run the experiment.  For example, when Fatemeh and I ran the pilot, I uploaded a treatmentcells.csv with batch="pilot" then when we ran the experiment I uploaded another csv with batch="exp1". 

You can upload treatmentcells.csv by replecing the example file with your own and using django's manage.py commands.

```
(venv)$ python manage.py import_treatmentcells
```

IMPORTANT: everytime you have a new batch of treatmentcells you need change 1 variable in the worker.py script.  On line 15 the variable `_BATCH` should be changed to whatever the batchname is, match case and everything.


### Exporting data
You can export data using the manage.py command
```
(venv)$ python manage.py export
```

This can take a while.  If you want to only export certain information you can comment out lines under
```
def handle(self, *args, **options):
```
in csr2/data/management/commands/export.py
