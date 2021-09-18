# Project Manager

## Description

Project Manager is, as the name suggests, a project management system (inspired in Git) that provides useful functionalities for clients, contractors, and project managers. It was my final project for CS50w; "a complex dynamic website which uses Django on the back-end and JavaScript on the front-end".

### Clients

Project Manager allows clients to see in detail the evolution of their project, including short descriptions and images of the work currently in progress, as well as PDF documents, which may include reports or, well, virtually anything! Clients, as well as all users, may 'check' any Commit or Document by clicking a green `read` button on the right of it, to signal to themselves they have already read the information present on that specific section and to not worry about it any longer.

### Foremen/Managers/Workers

Project Manager allows foremen, managers, and workers to commit the evolution of some project in a Git-style system. The commit system includes taking pictures with a handheld cellphone, making it even easier to upload images. Foremen and managers may create, edit, and remove commits (and their images), documents, as well as editing project names, descriptions, banners, and even archiving projects.

### Engineers/Supervisors/Overseers

Project Manager allows engineers, supervisors, and overseers to manage all work currently in progress to the project. Unlike foremen, engineers have special admin privileges, being members of the Django `staff` group in the admin panel, in addition to inheriting all permissions of the former group. As well as adding and removing project managers in each project, engineers can manage other users and their groups, being able, for example, to add new members of the team, which were recently registered, or remove them or their privileges.

## Installation: How to

To install the project and run it, there are only 3 basic steps to follow:

First of all, navigate to your desired installation folder. Then, run

```shell
git clone https://github.com/zaymuel/project-manager
```

This will create a folder inside your parent directory called `project-manager`. Next, run

```shell
cd project-manager
```

to move your console to the newly created folder where the project lives. Now that our project is cloned into your computer and we are on its root folder, we run `pip` to verify your local dependencies, and install the necessary ones:

```shell
python -m pip install -r requirements.txt
```

And, now, we just have to actually run Python to take care of our local server! From now on, every time you want to run the program, you only need to use the following command:

```shell
python manage.py runserver
```

This will output something like:

```shell
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

In which case you just need to follow the specified link (here, `http://127.0.0.1:8000/`). That's it! :tada:

## Contents

- `./.github` contains the CI YAML needed for GitHub Actions
- `./capstone` contains the overall `Project Manager` files (settings and such).
- `./media/` contains, as the name suggests, all media files relating to the project's models, structured in the following way:
  - `<projectname>/` contains all media files for the `projectname` Project model (documents and images):
    - `banners/` contains, if present, the banner for the `projectname` Project model,
    - `commits/` contains, if present, the images associated with the `image` field on the Commit model related to `projectname`,
    - `docs/` contains, if present, the documents associated with each `image` field on the Commit model related to the `projectname` Project model.
- `./projectmanager/` contains the specific files and settings for the `Project Manager` app:
  - `migrations/` contains the database migrations,
  - `static/` contains the static files (`JavaScript` scripts and `CSS` stylings),
  - `templates/` contains the `HTML` templates for all the different views in the project,
  - `models.py` contains the models needed for the application,
  - `tests.py` contains the tests required for GitHub Actions to validate the build,
  - `urls.py` contains the URL patterns and routes for the application,
  - `views.py` contains all views associated with each URL pattern.
- `./staticfiles/` contains collected static files by `manage.py` (just `django-admin` files & `styles.css`).
- `.gitignore` contains git ignored files (mainly cache files).
- `.db.sqlite3` contains the `SQLite` database needed for Django.
- `.manage.py` is the Django executable for commands.
- `.README.md` is this very file, which outlines the main parts of this project.
- `.requirements.txt` contains the required modules for the `Project Manager` project (`Django`, `Pillow`, `django-cleanup`, etc).

## Additional Information

As a Civil Engineering graduate, I thought of making this project so that, in the future, I may be able to implement it in the company I work in. This would make all the documentation for the work being done in the palm of the client's hand, as well as shortening the distance between customers and their construction projects.

## Justification

As my CS50w's final project, I must say it is a complex dynamic website that uses Django on the back-end and JavaScript on the front-end.

### JavaScript

JavaScript is used in:

- Fetching information from the database, via secure CSRF & HTTPS Django request integration,
  - Extracting the CSRF cookie from the user's browser and adding it to each request, thus eliminating the need for a `@csrf_exempt` call in each JSON Django view.
- Okay'ing commits & documents. A button is presented to the user, allowing him to mark specific commits/documents he has already seen,
- (Managers) Editing commit & document information messages,
- (Managers) Deleting:
  - commits,
  - commit images,
  - documents.
- (Managers) Editing project name, description, and archiving & unarchiving projects.

### Django

Meanwhile, Django, via Python, is used in:

- Handling normal HTTP `GET` & `POST` requests (standard),
- Handling JSON `GET`, `PUT` & `POST` requests,
- Registering new users,
- Maintaining the database & logic of the application,
  - Organizing the models,
  - Generating forms for each model,
  - Querying the database,
    - Making `Q`-queries,
  - Handling database transactions (updates, insertions, deletions).
- Handling files (documents & images) uploaded to compose some project's annexes;
  - Database integration,
  - Native file storage & maintenance,
  - Deleting unused files (which were linked by a recently deleted Commit/Document), powered by the `django-cleanup` module.
- Defining Users as either staff (Engineers, Foremen/Managers) or Clients,
