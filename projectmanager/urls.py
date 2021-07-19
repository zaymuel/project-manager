from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("project/<str:client>/<str:projID>/", views.viewproject, name="viewproject"),
    # get okay-checked commit & docs IDs
    path("okays/<int:projID>/", views.checked_posts, name="checked_posts"),
    # add okay-check to commit & docs ID
    path("okay/<int:postID>/", views.okay_post, name="okay_post"),
    path("commit/", views.create_commit, name="create_commit"),
    re_path(r"^commit/(?P<postID>\d+)/$", views.create_commit, name="re_create_commit"),
    # edit text for document or commit
    path("edit/text/<int:postID>/", views.update_text, name="update_text"),
    # get image file
    path("get/image/<str:img_type>/<int:imgID>/", views.retrieve_image, name="retrieve_image"),
    # get document file
    path("get/document/<int:docID>/", views.retrieve_file, name="retrieve_file"),
    # edit file annexes for document or commit (image)
    path("edit/file/<int:postID>/", views.update_file, name="update_file"),
    path("documentupload/", views.upload_file, name="upload_file"),
    re_path(r"^documentupload/(?P<postID>\d+)/$", views.upload_file, name="re_upload_file"),
    path("delete/<int:postID>/", views.delete_post, name="delete_post"),
    path("newproject/", views.create_project, name="create_project"),
    path("archived/", views.archived_projects, name="archived_projects"),
    path("archive/<int:projID>/", views.archive_project, name="archive_project"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register")
]
