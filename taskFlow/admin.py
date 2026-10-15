from django.contrib import admin
from django.contrib.auth.models import User

from taskFlow.models import AccountVerification, Issue

admin.site.register(Issue)
admin.site.register(AccountVerification)

admin.site.unregister(User)
admin.site.register(User)
