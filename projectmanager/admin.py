from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Commit, Document, UserViewedCommit, UserViewedDocument


class ProjectAdmin(admin.ModelAdmin):
    filter_horizontal = ("managers",)


admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Commit)
admin.site.register(Document)
admin.site.register(UserViewedCommit)
admin.site.register(UserViewedDocument)
