import os
from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    pass

    def is_client(self):
        # If user has a group
        if self.groups.filter().exists():
            # Evaluate if he is in the Client group
            return bool(self.groups.filter(name="Client"))

        # User is, for all effects, a client w/o privileges
        return True


def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/banners/<projectname>/<filename>
    return f'{instance.shortname}/banners/{filename}'


class Project(models.Model):
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects", db_index=True)
    # Has to be Char, not Text, for MySQL compatibility reasons
    shortname = models.CharField(unique=True, max_length=64, db_index=True)
    # Image banner of the project
    banner = models.ImageField(upload_to=project_directory_path, blank=True)
    description = models.TextField(max_length=1024)
    managers = models.ManyToManyField(
        User, related_name="managing", blank=True, db_index=True)
    active = models.BooleanField(default=True)

    def commit_count(self):
        return int(self.commits.count())

    def __str__(self):
        return f"{self.pk}: {self.client}'s '{self.shortname}' project: '{self.description[:20]}'"


def commit_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/commits/<projectname>/<filename>
    return f'{instance.project.shortname}/commits/{filename}'


class Commit(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="commits", db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_commits", db_index=True)
    message = models.CharField(max_length=128)
    # annex documents field
    image = models.ImageField(upload_to=commit_directory_path, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}: {self.user} on '{self.project.shortname}' project: '{self.message[:20]}' @ {self.timestamp}"


class UserViewedCommit(models.Model):
    commit = models.OneToOneField(
        Commit, on_delete=models.CASCADE, related_name="okays", db_index=True)
    users = models.ManyToManyField(
        User, related_name="viewed_commits", blank=True, db_index=True)


def doc_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/docs/<projectname>/<filename>
    return f'{instance.project.shortname}/docs/{filename}'


def validate_file_extension(value):
    if value.file.content_type != 'application/pdf':
        raise ValidationError('File is not PDF.')


class Document(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="documents", db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_documents", db_index=True)
    message = models.CharField(max_length=128)
    # annex documents field
    document = models.FileField(upload_to=doc_directory_path,
                                validators=[
                                    validate_file_extension,
                                    FileExtensionValidator(
                                        ["pdf"], 'Please upload a PDF version of the file.')
                                ])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}: {self.user} on '{self.project.shortname}' project: '{self.message[:20]}' at {self.timestamp}"


class UserViewedDocument(models.Model):
    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, related_name="okays", db_index=True)
    users = models.ManyToManyField(
        User, related_name="viewed_documents", blank=True, db_index=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('client', 'shortname', 'banner', 'description', 'managers')
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'shortname': forms.Textarea(attrs={'class': 'form-control', 'cols': 10, 'rows': 2}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 80, 'rows': 20}),
            'managers': forms.CheckboxSelectMultiple(),
        }


class CommitForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=Project.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        super(CommitForm, self).__init__(*args, **kwargs)
        if not user.is_staff:
            self.fields['project'].queryset = Project.objects.filter(
                active=True).filter(managers=user).order_by("pk").all()

    class Meta:
        model = Commit
        fields = ('project', 'message', 'image')

        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'cols': 80, 'rows': 20}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class DocumentForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=Project.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        if not user.is_staff:
            self.fields['project'].queryset = Project.objects.filter(
                active=True).filter(managers=user).order_by("pk").all()

    class Meta:
        model = Document
        fields = ('project', 'message', 'document')

        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'cols': 80, 'rows': 20}),
            'document': forms.ClearableFileInput(
                attrs={'class': 'form-control',
                       'accept': '.pdf', 'required': True}
            ),
        }

        labels = {
            'document': 'PDF Document upload',
        }
