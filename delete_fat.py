import website.wsgi

from data.models import Mturker

m = Mturker.objects.get(mturkid='A30ZN31ZPFCE2N')
m.user.delete()
m.delete()
