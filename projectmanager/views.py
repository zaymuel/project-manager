import os
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import FileResponse, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from PIL import Image

from .models import User, Project, Commit, Document, UserViewedCommit, ProjectForm, CommitForm, DocumentForm, UserViewedDocument


def index(request):
    """
    If user authenticated, displays all projects user is allowed to see.
    Else, displays welcome page
    """

    if request.user.is_authenticated:
        # all project user is allowed to see
        if request.user.is_staff:
            projects = Project.objects.filter(
                active=True).order_by("shortname").all()
        else:
            projects = Project.objects.filter(active=True).filter(
                Q(client=request.user) | Q(managers=request.user)
            ).distinct().select_related('client').all()

        return render(request, "projectmanager/allprojects.html", {
            'projects': projects, "active": True
        })

    # welcome page
    return render(request, "projectmanager/index.html")


@login_required
def viewproject(request, client, projID):
    """
    Displays page with requested project's details.
    """
    # Get client's User model
    try:
        projClient = User.objects.get(username=client)
    except User.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             f"Project \"{projID}\" does not exist under user \"{client}\"")
        return HttpResponseRedirect(reverse('index'))

    # Try to get Project model under retrieved User
    try:
        project = Project.objects.get(client=projClient, shortname=projID)
    except Project.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             f"Project \"{projID}\" does not exist")
        return HttpResponseRedirect(reverse('index'))

    return render(request, "projectmanager/project.html", {
        'project': project
    })


@login_required
def checked_posts(request, projID):
    """
    Returns specific user's checked (reviewed) posts (commits & documents).
    """

    if request.method == "GET":
        if projID is None:
            return JsonResponse({"error": "Please enter project ID."}, status=400)

        try:
            # Query for project
            checkedproj = Project.objects.get(pk=projID)
        except Project.DoesNotExist:
            # Error: project does not exist
            return JsonResponse({"error": "Project ID does not exist."}, status=400)

        user = request.user
        okaycommitlist = [c for c in user.viewed_commits.filter(
            commit__in=checkedproj.commits.all())]
        okaydocumentlist = [c for c in user.viewed_documents.filter(
            document__in=checkedproj.documents.all())]

        # This gets all checked commits for this single project
        # print([c for c in user.viewed_commits.filter(commit__in=checkedproj.commits.all())])

        # This gets all checked commits for ALL projects
        # print([c for c in user.viewed_commits.all()])

        if len(okaycommitlist) == 0:
            okaycommitlist = None
        if len(okaydocumentlist) == 0:
            okaydocumentlist = None

        # return okay'd commits' ID's
        return JsonResponse({
            "project": projID,
            "okayCommitIDs": [okay.commit.pk for okay in okaycommitlist] if okaycommitlist else okaycommitlist,
            "okayDocumentIDs": [okay.document.pk for okay in okaydocumentlist] if okaydocumentlist else okaydocumentlist,
        }, safe=False)

    # Request method must be via GET
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def okay_post(request, postID):
    """
    Receives PUT request and registers okay in commit or document.
    """
    if request.method == "PUT":
        # see if doc or commit to modify
        typeofpost = json.loads(request.body).get("type")
        if typeofpost not in ["commit", "document"]:
            return JsonResponse({"error": "Post type not supported."}, status=400)

        data = json.loads(request.body).get("okay")
        if data is None:
            return JsonResponse({"error": "Must enter okay or not okay."}, status=400)

        if typeofpost == "commit":
            try:
                # Query for requested commit
                commit = Commit.objects.get(pk=postID)
            except Commit.DoesNotExist:
                return JsonResponse({"error": "Commit not found."}, status=404)

            try:
                # Query for requested UserViewedCommit
                userviewedcommit = UserViewedCommit.objects.get(commit=commit)
            except UserViewedCommit.DoesNotExist:
                # If Commit has no okaylist, create one
                userviewedcommit = UserViewedCommit.objects.create(
                    commit=commit)

            if data == 'true':
                # Add okay to commit
                userviewedcommit.users.add(request.user)
                # print(request.user.viewed_commits.filter(commit=commit))
            else:
                # Remove okay from commit
                userviewedcommit.users.remove(request.user)
                # print(request.user.viewed_commits.filter(commit=commit))

        elif typeofpost == "document":
            try:
                # Query for requested document
                document = Document.objects.get(pk=postID)
            except Document.DoesNotExist:
                return JsonResponse({"error": "Document not found."}, status=404)

            try:
                # Query for requested UserViewedDocument
                uservieweddoc = UserViewedDocument.objects.get(
                    document=document)
            except UserViewedDocument.DoesNotExist:
                # If Document has no okaylist, create one
                uservieweddoc = UserViewedDocument.objects.create(
                    document=document)

            if data == 'true':
                # Add okay to document
                uservieweddoc.users.add(request.user)
                # print(request.user.viewed_commits.filter(commit=commit))
            else:
                # Remove okay from commit
                uservieweddoc.users.remove(request.user)
                # print(request.user.viewed_commits.filter(commit=commit))

        return HttpResponse(status=204)

    # Request method must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@login_required
def create_commit(request, postID=""):
    # Disallow clients to enter screen
    if request.user.is_client():
        messages.add_message(
            request, messages.ERROR, "Please note only staff members may create commits.")
        return HttpResponseRedirect(reverse("index"))

    if request.method == 'POST':
        getuser = Commit(user=request.user)
        f = CommitForm(request.user, request.POST,
                       request.FILES, instance=getuser)
        if f.is_valid():
            # See if project is active
            if f.cleaned_data["project"].active:
                # returns saved commit
                finalcommit = f.save()

                # image optimization
                if finalcommit.image:
                    image = Image.open(finalcommit.image.path)
                    image.save(finalcommit.image.path,
                               quality=75, optimize=True)

                # IMPLEMENT SENDING EMAIL TO CLIENT

                messages.add_message(request, messages.SUCCESS,
                                     "Commit successfully added!")

                return HttpResponseRedirect(reverse('viewproject',
                                                    args=[
                                                        finalcommit.project.client,
                                                        finalcommit.project.shortname
                                                    ])
                                            )
                # return HttpResponseRedirect(f'/project/{finalcommit.project.client}/{finalcommit.project.shortname}')

            else:
                # project is archived, unable to commit
                messages.add_message(request, messages.ERROR,
                                     "Sorry, but that project is archived. \
                                        To create a new commit in it, please make it active again.")
                return HttpResponseRedirect(reverse('index'))
        else:
            messages.add_message(request, messages.ERROR,
                                 f"Unable to create commit: {f.errors.as_text()}")
            return render(request, "projectmanager/newcommit.html", {'form': f})
    else:
        # GET request
        if postID:
            try:
                reqproject = Project.objects.get(pk=postID)
            except Project.DoesNotExist:
                return HttpResponseRedirect(reverse("create_commit"))
            else:
                projectid = Commit(project=reqproject)
                f = CommitForm(request.user, instance=projectid)

        else:
            f = CommitForm(request.user)

        return render(request, "projectmanager/newcommit.html", {'form': f})


@login_required
def update_text(request, postID):
    """
    Receives a POST request and updates commit/document TEXT in DB.
    """
    # Disallow clients to enter screen
    if request.user.is_client():
        return JsonResponse({"error": "Please note only staff members may update texts."}, status=400)

    # Request must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # see if doc or commit to modify
    typeofpost = json.loads(request.body).get("type")
    if typeofpost not in ["commit", "document", "projectName", "projectDescription"]:
        return JsonResponse({"error": "Post type not supported."}, status=400)

    # Get JSON data & updated text
    edittext = json.loads(request.body).get("text")

    if edittext is None:
        return JsonResponse({"error": "Must enter okay or not okay."}, status=400)
    if edittext == "":
        return JsonResponse({"error": "Unable to post. Please enter some text."}, status=400)

    if typeofpost == "projectName":
        if len(edittext) > 64:
            return JsonResponse({"error": "Unable to post. Please enter less text."}, status=400)
        try:
            Project.objects.get(pk=postID)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project does not exist"}, status=400)

        # Update Project
        Project.objects.filter(pk=postID).update(shortname=edittext)

        return JsonResponse({
            "message": "Project name successfully edited! Please find the new project screen on the following page."
        }, status=201)

    elif typeofpost == "projectDescription":
        if len(edittext) > 1024:
            return JsonResponse({"error": "Unable to post. Please enter less text."}, status=400)
        try:
            Project.objects.get(pk=postID)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project does not exist"}, status=400)

        # Update Project
        Project.objects.filter(pk=postID).update(description=edittext)

        return JsonResponse({"message": "Project description successfully edited!"}, status=201)

    if len(edittext) > 128:
        return JsonResponse({"error": "Unable to post. Please enter less text."}, status=400)

    if typeofpost == "commit":
        try:
            Commit.objects.get(pk=postID)
        except Commit.DoesNotExist:
            return JsonResponse({"error": "Commit does not exist"}, status=400)

        # Update Post
        Commit.objects.filter(pk=postID).update(message=edittext)

        return JsonResponse({"message": "Successfully edited!"}, status=201)

    elif typeofpost == "document":
        try:
            Document.objects.get(pk=postID)
        except Document.DoesNotExist:
            return JsonResponse({"error": "Document does not exist"}, status=400)

        # Update Post
        Document.objects.filter(pk=postID).update(message=edittext)

        return JsonResponse({"message": "Successfully edited!"}, status=201)


@login_required
def retrieve_image(request, img_type, imgID):
    """
    Receives a HTTP GET request and retrieves project banner or commit image with that ID as inline.
    """
    if img_type not in ["banner", "commit"]:
        messages.add_message(
            request, messages.ERROR, "Invalid file type.")
        return HttpResponseRedirect(reverse("index"))

    if request.user.is_authenticated:
        # admins can see all images
        if request.user.is_staff:
            if img_type == "banner":
                try:
                    requested_project_model = Project.objects.get(pk=imgID)
                    # if present, returns banner for inline presentation
                    response = FileResponse(requested_project_model.banner,)

                # ValueError if banner does not exist
                except ValueError or Project.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Image banner does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                else:
                    response["Content-Disposition"] = "inline"
                    return response

            elif img_type == "commit":
                try:
                    requested_commit_model = Commit.objects.get(pk=imgID)
                    # if present, returns commit image for inline presentation
                    response = FileResponse(requested_commit_model.image,)

                # ValueError if commit image does not exist
                except ValueError or Commit.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Commit image does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                else:
                    response["Content-Disposition"] = "inline"
                    return response

        # if user is not client, can be manager
        elif not request.user.is_client():
            # get all projects user is manager in, and see if current is one of them
            if img_type == "banner":
                try:
                    requested_project_model = Project.objects.get(pk=imgID)
                    # if present, get banner
                    response = FileResponse(requested_project_model.banner,)

                except ValueError or Project.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Image banner does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                if requested_project_model in request.user.managing.all():
                    # positive case: return banner for inline presentation
                    response["Content-Disposition"] = "inline"
                    return response
                # negative case: user does not manage this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

            elif img_type == "commit":
                try:
                    requested_commit_model = Commit.objects.get(pk=imgID)
                    # if present, returns commit image for inline presentation
                    response = FileResponse(requested_commit_model.image,)

                except ValueError or Commit.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Commit image does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                if requested_commit_model.project in request.user.managing.all():
                    # positive case: return banner for inline presentation
                    response["Content-Disposition"] = "inline"
                    return response
                # negative case: user does not manage this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

        # if user is client
        else:
            if img_type == "banner":
                try:
                    requested_project_model = Project.objects.get(pk=imgID)
                    # if present, get banner
                    response = FileResponse(requested_project_model.banner,)

                except ValueError or Project.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Image banner does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                # get all projects user is client in,
                # and see if current is one of them
                if requested_project_model in request.user.projects.all():
                    # positive case: return banner for inline presentation
                    response["Content-Disposition"] = "inline"
                    return response
                # negative case: user is not a client of this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

            elif img_type == "commit":
                try:
                    requested_commit_model = Commit.objects.get(pk=imgID)
                    # if present, returns commit image for inline presentation
                    response = FileResponse(requested_commit_model.image,)

                except ValueError or Commit.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         "Commit image does not exist.")
                    return HttpResponseRedirect(reverse("index"))

                # get all projects user is client in,
                # and see if current is one of them
                if requested_commit_model.project in request.user.projects.all():
                    # positive case: return banner for inline presentation
                    response["Content-Disposition"] = "inline"
                    return response
                # negative case: user is not a client of this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

    else:
        messages.add_message(request, messages.ERROR,
                             "Authentication error. Please log in to see files.")
        return HttpResponseRedirect(reverse("index"))


@login_required
def retrieve_file(request, docID):
    """
    Receives a HTTP GET request and retrieves document with that ID as download.
    """

    if request.user.is_authenticated:
        # admins can download all files
        if request.user.is_staff:
            try:
                documentmodel = Document.objects.get(pk=docID)
            except Document.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     "Document does not exist.")
                return HttpResponseRedirect(reverse("index"))

            # Split the elements of the path
            path, file_name = os.path.split(documentmodel.document.__str__())

            # returns document for download
            response = FileResponse(documentmodel.document,)
            response["Content-Disposition"] = "attachment; filename=" + file_name

            return response

        # if user is not client, can be manager
        elif not request.user.is_client():
            try:
                documentmodel = Document.objects.get(pk=docID)
            except Document.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     "Document does not exist.")
                return HttpResponseRedirect(reverse("index"))

            # get all projects user is manager in,
            # and see if current is one of them
            if documentmodel.project in request.user.managing.all():
                # positive case: return document

                # Split the elements of the path
                path, file_name = os.path.split(
                    documentmodel.document.__str__())
                # returns document for download
                response = FileResponse(documentmodel.document,)
                response["Content-Disposition"] = "attachment; filename=" + file_name
                return response
            else:
                # negative case: user does not manage this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

        # if user is client
        else:
            try:
                documentmodel = Document.objects.get(pk=docID)
            except Document.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     "Document does not exist.")
                return HttpResponseRedirect(reverse("index"))

            # get all projects user is client in,
            # and see if current is one of them
            if documentmodel.project in request.user.projects.all():
                # positive case: return document

                # Split the elements of the path
                path, file_name = os.path.split(
                    documentmodel.document.__str__())
                # returns document for download
                response = FileResponse(documentmodel.document,)
                response["Content-Disposition"] = "attachment; filename=" + file_name
                return response
            else:
                # negative case: user does not manage this project
                messages.add_message(
                    request, messages.ERROR, "Sorry, you are unauthorized to see this file.")
                return HttpResponseRedirect(reverse("index"))

    else:
        messages.add_message(request, messages.ERROR,
                             "Authentication error. Please log in to see files.")
        return HttpResponseRedirect(reverse("index"))


@login_required
def update_file(request, postID):
    """
    Receives a HTTP POST request and updates commit/document file annex in DB.
    """
    # Disallow clients to enter screen
    if request.user.is_client():
        messages.add_message(request, messages.ERROR,
                             "Please note only staff members may update files.")
        return HttpResponseRedirect(reverse("index"))

    # Request must be via POST
    if request.method != "POST":
        messages.add_message(request, messages.ERROR, "POST request required!")
        return HttpResponseRedirect(reverse("index"))

    # see if doc or commit to modify
    typeofpost = request.POST.get("type")
    if typeofpost not in ["commit", "document", "project"]:
        messages.add_message(request, messages.ERROR,
                             "Post type not supported.")
        return HttpResponseRedirect(reverse("index"))

    # see if doc or commit to modify
    typeofalteration = request.POST.get("modify")
    if typeofalteration != "modify":
        messages.add_message(request, messages.ERROR, "Command not supported.")
        return HttpResponseRedirect(reverse("index"))

    if typeofpost == "commit":
        try:
            modcommit = Commit.objects.get(pk=postID)
        except Commit.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 "Commit does not exist.")
            return HttpResponseRedirect(reverse("index"))

        # Update Post
        modcommit.image = request.FILES.get("uploadedFile")
        modcommit.save()

        # image optimization
        if modcommit.image:
            image = Image.open(modcommit.image.path)
            image.save(modcommit.image.path, quality=75, optimize=True)

        messages.add_message(request, messages.SUCCESS,
                             "Commit image successfully updated!")

        return HttpResponseRedirect(f'/project/{modcommit.project.client}/{modcommit.project.shortname}#commit-{modcommit.pk}')

    elif typeofpost == "document":
        try:
            moddoc = Document.objects.get(pk=postID)
        except Document.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 "Document does not exist.")
            return HttpResponseRedirect(reverse("index"))

        # Update Post
        moddoc.document = request.FILES.get("uploadedFile")
        moddoc.save()
        messages.add_message(request, messages.SUCCESS,
                             "Document successfully updated!")
        return HttpResponseRedirect(f'/project/{moddoc.project.client}/{moddoc.project.shortname}#doc-{moddoc.pk}')

    elif typeofpost == "project":
        try:
            modproj = Project.objects.get(pk=postID)
        except Project.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 "Project does not exist.")
            return HttpResponseRedirect(reverse("index"))

        # Update proj image banner
        modproj.banner = request.FILES.get("uploadedFile")
        modproj.save()

        # image optimization
        if modproj.banner:
            image = Image.open(modproj.banner.path)
            image.save(modproj.banner.path, quality=75, optimize=True)

        messages.add_message(request, messages.SUCCESS,
                             "Project Image Banner successfully updated!")
        return HttpResponseRedirect(reverse('viewproject',
                                            args=[
                                                modproj.client,
                                                modproj.shortname
                                            ])
                                    )
        # return HttpResponseRedirect(f'/project/{modproj.client}/{modproj.shortname}')

    return JsonResponse({"error": "Something's gone wrong. Please try again"}, status=400)


@login_required
def upload_file(request, postID=""):
    # Disallow clients to enter screen
    if request.user.is_client():
        messages.add_message(request, messages.ERROR,
                             "Please note only staff members may add new files.")
        return HttpResponseRedirect(reverse("index"))

    if request.method == 'POST':
        getuser = Document(user=request.user)
        d = DocumentForm(request.user, request.POST,
                         request.FILES, instance=getuser)
        if d.is_valid():
            # See if project is active
            if d.cleaned_data["project"].active:
                # returns saved document
                docupload = d.save()

                # IMPLEMENT SENDING EMAIL TO CLIENT

                messages.add_message(request, messages.SUCCESS,
                                     "Document successfully uploaded!")
                return HttpResponseRedirect(reverse('viewproject',
                                                    args=[
                                                        docupload.project.client,
                                                        docupload.project.shortname
                                                    ])
                                            )
                # return HttpResponseRedirect(f'/project/{docupload.project.client}/{docupload.project.shortname}')

            else:
                # project is archived, unable to commit
                messages.add_message(request, messages.ERROR,
                                     "Sorry, but that project is archived. \
                                        To create a new document in it, please make it active again.")
                return HttpResponseRedirect(reverse("index"))

        else:
            messages.add_message(
                request, messages.ERROR, f"Unable to upload document: {d.errors.as_text()}")
            return render(request, "projectmanager/newdocument.html", {'form': d})

    else:
        # GET request
        if postID:
            try:
                reqproject = Project.objects.get(pk=postID)
            except Project.DoesNotExist:
                return HttpResponseRedirect(reverse("upload_file"))
            else:
                projectid = Document(project=reqproject)
                d = DocumentForm(request.user, instance=projectid)
        else:
            d = DocumentForm(request.user)

        return render(request, "projectmanager/newdocument.html", {'form': d})


@login_required
def delete_post(request, postID):
    """
    Receives a JSON POST request and deletes commit/document in DB.
    """
    # Disallow clients to enter screen
    if request.user.is_client():
        return JsonResponse({"error": "Please note only staff members may delete posts."}, status=400)

    # Request must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # see if doc or commit to delete
    typeofpost = json.loads(request.body).get("type")
    if typeofpost not in ["commit/image", "commit", "document", "projectBanner"]:
        return JsonResponse({"error": "Post type not supported."}, status=400)

    confirmation = json.loads(request.body).get("remove")
    if confirmation != "remove":
        return JsonResponse({"error": "Command not supported."}, status=400)

    if typeofpost == "document":
        try:
            moddoc = Document.objects.get(pk=postID)
        except Document.DoesNotExist:
            return JsonResponse({"error": "Document does not exist"}, status=400)

        moddoc.delete()
        return JsonResponse({"message": "Document successfully deleted!"}, status=201)

    elif typeofpost == "commit/image" or typeofpost == "commit":
        try:
            modcommit = Commit.objects.get(pk=postID)
        except Commit.DoesNotExist:
            return JsonResponse({"error": "Commit does not exist"}, status=400)

        if typeofpost == "commit":
            # Delete entire commit
            modcommit.delete()
            return JsonResponse({"message": "Commit successfully deleted!"}, status=201)
        else:
            # Delete just commit image
            modcommit.image.delete()
            modcommit.save()
            return JsonResponse({"message": "Commit image successfully removed!"}, status=201)

    elif typeofpost == "projectBanner":
        try:
            modproj = Project.objects.get(pk=postID)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project does not exist"}, status=400)

        modproj.banner.delete()
        modproj.save()
        return JsonResponse({"message": "Project Image Banner successfully deleted!"}, status=201)

    return JsonResponse({"error": "Something's gone wrong. Please try again"}, status=400)


@login_required
def archive_project(request, projID):
    """
    Receives a JSON POST request and archives project.
    """
    # Disallow clients to enter screen
    if request.user.is_client():
        return JsonResponse({"error": "Please note only staff members may delete posts."}, status=400)

    # Request must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    confirmation = json.loads(request.body).get("archive")
    if confirmation not in ["archive", "unarchive"]:
        return JsonResponse({"error": "Command not supported."}, status=400)

    try:
        Project.objects.get(pk=projID)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project does not exist"}, status=400)

    if confirmation == "archive":
        # Archive Project
        Project.objects.filter(pk=projID).update(active=False)
        return JsonResponse({"message": "Project successfully archived!"}, status=201)
    elif confirmation == "unarchive":
        # Unarchive Project
        Project.objects.filter(pk=projID).update(active=True)
        return JsonResponse({"message": "Project successfully active again!"}, status=201)


@login_required
def create_project(request):
    # Disallow clients to enter screen
    if request.user.is_client():
        messages.add_message(
            request, messages.ERROR, "Please note only staff members may add new project.")
        return HttpResponseRedirect(reverse("index"))

    if request.method == 'POST':
        p = ProjectForm(request.POST, request.FILES)
        if p.is_valid():
            # returns saved (new) project
            createdproject = p.save()

            # image optimization
            if createdproject.banner:
                image = Image.open(createdproject.banner.path)
                image.save(createdproject.banner.path,
                           quality=75, optimize=True)

            # IMPLEMENT SENDING EMAIL TO CLIENT

            messages.add_message(request, messages.SUCCESS,
                                 "Project successfully added!")
            return HttpResponseRedirect(reverse('viewproject',
                                                args=[
                                                    createdproject.client,
                                                    createdproject.shortname
                                                ])
                                        )
            # return HttpResponseRedirect(f'/project/{createdproject.client}/{createdproject.shortname}')
        else:
            messages.add_message(
                request, messages.ERROR, f"Unable to create project: {p.errors.as_text()}")
            return render(request, "projectmanager/newproject.html", {'form': p})
    else:
        # GET request
        p = ProjectForm()

    return render(request, "projectmanager/newproject.html", {'form': p})


@login_required
def archived_projects(request):
    """
    If user authenticated, displays all archived projects user is allowed to see.
    """
    if request.user.is_staff:
        # if user is admin, allow every project
        projects = Project.objects.filter(
            active=False).order_by("shortname").all()
    else:
        # all project user is allowed to see
        projects = Project.objects.filter(active=False).filter(
            Q(client=request.user) | Q(managers=request.user)
        ).distinct().select_related('client').all()

    return render(request, "projectmanager/allprojects.html", {
        'projects': projects, "active": False,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid username and/or password.")
            return render(request, "projectmanager/login.html")
    else:
        return render(request, "projectmanager/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        first = request.POST.get("firstname").strip()
        last = request.POST.get("lastname").strip()

        client = request.POST.get("client")

        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if not email or not first or not last or not password or not confirmation:
            messages.add_message(request, messages.ERROR,
                                 "Please enter all required fields.")
            return render(request, "projectmanager/register.html")

        # Validate email address
        try:
            validator = EmailValidator()
            validator(email)
        except ValidationError:
            messages.add_message(request, messages.ERROR,
                                 f"Please note \"{email}\" is not a valid email address.")
            return render(request, "projectmanager/register.html")

        # Ensure password matches confirmation
        if password != confirmation:
            messages.add_message(request, messages.ERROR,
                                 "Passwords must match.")
            return render(request, "projectmanager/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=email, email=email, password=password, first_name=first, last_name=last)
            user.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR,
                                 "Sorry, username already taken.")
            return render(request, "projectmanager/register.html")
        # Make all new users inactive
        # This way, they cannot log in
        # Except if given explicit permission by admin
        user.is_active = False
        user.save()

        if client:
            Group.objects.get(name="Client").user_set.add(user)
            messages.add_message(request, messages.SUCCESS,
                                 "User successfully created!")
            messages.add_message(request, messages.INFO,
                                 "Now, please give us some time to confirm your identity.")
        else:
            messages.add_message(request, messages.INFO,
                                 "Please note you will have to wait until the admin puts you in a group.")

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "projectmanager/register.html")
