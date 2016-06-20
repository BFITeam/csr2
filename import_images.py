import website.wsgi
from data.models import Image
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGEDIR = os.path.join(ROOT, 'images')

files = os.listdir(IMAGEDIR)
for f in files:
    if ".jpg" in f:
        batch = f.split('.')[0][-1]
        newfile, created = Image.objects.get_or_create(filename=f, batch=batch)
