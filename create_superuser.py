from django.contrib.auth.models import User

superuser = User.objects.create_superuser("admin", "teddy171X@outlook.com", "FDPX_admin")
superuser.save()