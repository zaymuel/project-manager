document.addEventListener("DOMContentLoaded", function () {
  // Get Project ID
  userOkayS(Number(getProjectID()));
  // load index
});

function getProjectID() {
  return document.getElementById("projectID").dataset.id;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");
var userOkayCommitsId = new Set()
var userOkayDocumentsId = new Set()

async function getLikes(projID) {
  // Register okays in global variables
  const request = new Request(`/okays/${projID}/`, {
    headers: { "X-CSRFToken": csrftoken },
  });
  return await fetch(request, {
    method: "GET",
    mode: "same-origin", // Do not send CSRF token to another domain.
  })
    .then((response) => response.json())
    .then(function (response) {
      // if not null
      if (response.okayCommitIDs) {
        userOkayCommitsId = new Set(response.okayCommitIDs);
      } else {
        userOkayCommitsId = new Set()
      }
      // if not null
      if (response.okayDocumentIDs) {
        userOkayDocumentsId = new Set(response.okayDocumentIDs);
      } else {
        userOkayDocumentsId = new Set()
      }
    })
    .catch((error) => console.error(error));

      /* debugging tools
      if (response.okayCommitIDs.length === 0) {
        console.log("user has 0 okay commits");
      } else {
        console.log(`user has ${response.okayCommitIDs.length} okay commits`);
      }*/
}

async function userOkayS(projID) {
  await getLikes(projID)
  await this.putLikesOnPosts();
}

function putLikesOnPosts() {
  var commitList = document.querySelectorAll(".commit")
  if (commitList.length != 0) {
    commitList.forEach((commit) => {
      okayButtons(Number(commit.dataset.id), "commit");
    });
  }

  var documentList = document.querySelectorAll(".document")
  if (documentList.length != 0) {
    documentList.forEach((document) => {
      okayButtons(Number(document.dataset.id), "document");
    });
  }
}

function okayButtons(postID, type) {
  types = ["commit", "document"];
  if (!types.includes(type)) {
    alert("post type not supported");
  }

  btn = document.createElement("button");

  // commits
  if (type === "commit") {
    if (userOkayCommitsId.has(postID)) {
      // User has already okay'd commit
      btn.innerHTML = `read ✅`;
      btn.classList = `btn btn-success`;
      // Offer to un-okay commit
      btn.addEventListener("click", function () {
        postSetRead("commit", postID, false);
      });
    } else {
      // User has not okay'd commit
      btn.innerHTML = `read ❌`;
      btn.classList = `btn btn-outline-success`;
      // Offer to okay
      btn.addEventListener("click", function () {
        postSetRead("commit", postID, true);
      });
    }
  }
  // documents
  else if (type === "document") {
    if (userOkayDocumentsId.has(postID)) {
      // User has already okay'd document
      btn.innerHTML = `lido ✅`;
      btn.classList = `btn btn-success`;
      // Offer to un-okay document
      btn.addEventListener("click", function () {
        postSetRead("document", postID, false);
      });
    } else {
      // User has not okay'd document
      btn.innerHTML = `lido ❌`;
      btn.classList = `btn btn-outline-success`;
      // Offer to okay
      btn.addEventListener("click", function () {
        postSetRead("document", postID, true);
      });
    }
  }

  document.getElementById(`okay-${type}-${postID}`).lastChild.remove();
  document.getElementById(`okay-${type}-${postID}`).append(btn);
}

async function postSetRead(type, postID, yayornay) {
  const request = new Request(`/okay/${postID}/`, {
    headers: { "X-CSRFToken": csrftoken },
  });

  await fetch(request, {
    method: "PUT",
    mode: "same-origin", // Do not send CSRF token to another domain.
    body: JSON.stringify({
      type: type,
      okay: `${yayornay ? true : false}`,
    }),
  })
    .catch(function (error) {
      console.error(`unable to set read; "${error}"`);
    });

  await this.userOkayS(Number(getProjectID()))
}

function editPost(type, postId) {
  types = ["commit", "document"];
  if (!types.includes(type)) {
    alert("post type not supported");
  }
  // Remove edit button
  document.getElementById(`edit-${type}-${postId}`).remove();
  if (type === "commit") {
    image = document.querySelector(`#commit-img-${postId}`);
    isdocument = false;
    if (image) {
      image = image.innerHTML;
    } else {
      image = false;
    }
  } else if (type === "document") {
    image = false;
    isdocument = true;
  }

  document.getElementById(`okay-${type}-${postId}`).remove();
  // Get paragraph element
  editing = document.getElementById(`text-${type}-${postId}`);
  // Extract text from it
  editText = editing.firstElementChild.innerHTML.trim();
  // Remove paragraph and add textarea
  editing.innerHTML = `
    <div class="accordion" id="accordion-${type}-${postId}">
      <div class="card">
        <div class="card-header" id="headingOne-${type}-${postId}">
          <h2 class="mb-0">
            <button class="btn btn-info btn-block text-left" type="button" data-toggle="collapse"
            data-target="#collapseOne-${type}-${postId}" aria-expanded="true" aria-controls="collapseOne-${type}-${postId}">
              Change Text
            </button>
          </h2>
        </div>
        <div id="collapseOne-${type}-${postId}" class="collapse show" aria-labelledby="headingOne-${type}-${postId}" data-parent="#accordion-${type}-${postId}">
          <div class="card-body">
              <form id="editForm-${type}-${postId}">
                  <label for="compose-${type}-${postId}">Edit 
                  ${isdocument ? "Document" : "Commit"} description</label>
                  <textarea class="form-control" id="compose-${type}-${postId}" 
                  placeholder="Enter new message" rows="5" maxlength="128">${editText}</textarea>
                  <div class="w-100 py-1"></div>
                  <div class="container-fluid text-right col">
                    <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                    <input type="submit" class="btn btn-primary"/>
                  </div>
              </form>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header" id="headingTwo-${type}-${postId}">
          <h2 class="mb-0">
            <button class="btn btn-info btn-block text-left collapsed" type="button" data-toggle="collapse"
            data-target="#collapseTwo-${type}-${postId}" aria-expanded="false" aria-controls="collapseTwo-${type}-${postId}">
              ${
                image
                  ? `Alter Commit Image`
                  : `${
                      isdocument
                        ? `Alter Uploaded Document (send new)`
                        : `Upload Commit Image`
                    }`
              }
            </button>
          </h2>
        </div>
        <div id="collapseTwo-${type}-${postId}" class="collapse" aria-labelledby="headingTwo-${type}-${postId}" data-parent="#accordion-${type}-${postId}">
          <div class="card-body">
              <form id="fileEditForm-${type}-${postId}" action="/edit/file/${postId}/"
              enctype="multipart/form-data" method="POST">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                <input type="hidden" name="type" value="${type}">
                <input type="hidden" name="modify" value="modify">
                <div class="container-fluid row">
                    <div class="container-fluid col-1 align-self-end">
                      <button id="clear-${postId}" class="btn btn-secondary btn-sm" type="button" disabled
                      onclick="document.getElementById(
                      'uploaded${
                        image
                          ? `CommitImg`
                          : `${isdocument ? `Document` : "Commit"}`
                      }-${postId}').value = '';
                      document.getElementById('clear-${postId}').disabled = true;">Clear File</button>
                    </div>
                    <div class="container-fluid col-11">
                    ${
                      image
                        ? // if image exists, offer to change
                          `<label for="uploadedCommitImg-${postId}">Change commit image</label>
                        <input type="file" id="uploadedCommitImg-${postId}" name="uploadedFile" 
                        accept="image/*" class="form-control">`
                        : `${
                            // else, check if document
                            isdocument
                              ? // is document, offer to change
                                `<label for="uploadedDocument-${postId}">Change Document</label>
                                <input type="file" id="uploadedDocument-${postId}" name="uploadedFile" 
                                accept="application/pdf" class="form-control">`
                              : // commit w/o image => offer to upload
                                `<label for="uploadedCommit-${postId}">Add new commit image</label>
                                <input type="file" id="uploadedCommit-${postId}" name="uploadedFile" 
                                accept="image/*" class="form-control">`
                          }`
                    }
                    </div>
                </div>
                <div class="w-100 py-1"></div>
                <div class="container row">
                  <div class="container-fluid text-left col">
                  ${
                    image
                      ? // if image, remove image
                        `<label for="remove-${postId}">Or</label>
                      <button class="btn btn-danger btn" type="button" id="remove-${postId}"
                      onclick="removeAnnex('commit/image', ${postId})">Remove Current Image</button>`
                      : ""
                  }
                  </div>
                  <div class="container-fluid text-right col">
                    <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                    <input type="submit" class="btn btn-primary"/>
                  </div>
                </div>
              </form>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header" id="headingThree-${type}-${postId}">
          <h2 class="mb-0">
            <button class="btn btn-info btn-block text-left" type="button" data-toggle="collapse"
            data-target="#collapseThree-${type}-${postId}" aria-expanded="false" aria-controls="collapseThree-${type}-${postId}">
              Delete ${
                isdocument
                  ? `Document`
                  : `Commit`
              }
            </button>
          </h2>
        </div>
        <div id="collapseThree-${type}-${postId}" class="collapse" aria-labelledby="headingThree-${type}-${postId}" data-parent="#accordion-${type}-${postId}">
          <div class="card-body">
              <form id="deleteForm-${type}-${postId}">
                  <label for="delete-${type}-${postId}">Do you wish to delete this 
                    ${isdocument ? "Document" : "Commit"}?</label>
                  <button class="btn btn-danger" type="button" id="archiveProject" onclick="removeAnnex('${type}', ${postId})">
                    Yes, delete this ${isdocument ? "Document" : "Commit"}
                  </button>
                  <div class="w-100 py-1"></div>
                  <div class="container-fluid text-right col">
                    <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                    <input type="submit" class="btn btn-primary"/>
                  </div>
              </form>
          </div>
        </div>
      </div>
    </div>
    <div class="w-100 py-2"></div>`;

  // See if image/document is present for upload
  seeIfDocumentPresent = document.querySelector(
    `#uploaded${
      image ? `CommitImg` : `${isdocument ? `Document` : "Commit"}`
    }-${postId}`
  ).value;
  if (!seeIfDocumentPresent) {
    // No file present, upload just text
    document.querySelector(`#editForm-${type}-${postId}`).onsubmit = () => {
      // Get text from textarea
      text = document.querySelector(`#compose-${type}-${postId}`).value;

      // Pass text to Poster handler
      updatePostText(type, text, postId);
      return false;
    };
  }

  document
    .querySelector(
      `#uploaded${
        image ? `CommitImg` : `${isdocument ? `Document` : "Commit"}`
      }-${postId}`
    )
    .addEventListener("change", () => {
      // Get text from textarea
      var innit = document.getElementById(
        `uploaded${
          image ? `CommitImg` : `${isdocument ? `Document` : "Commit"}`
        }-${postId}`
      ).value;
      if (innit !== "") {
        document.getElementById(`clear-${postId}`).disabled = false;
      }
    });
}

function editProject() {
  let type = "project";
  let projID = Number(getProjectID());

  // Remove edit button
  document.getElementById(`editProject`).remove();
  let image = Boolean(document.querySelector(`#projectImageBanner`))
  if (image) {
    image = true;
  } else {
    image = false;
  }
  let isProjArchived = Boolean(document.querySelector(`#projectArchived`))
  
  // Get project name + description & Extract text from it
  let projectName = document.getElementById(`projectName`).innerHTML.trim();
  let projectDescription = document
    .getElementById(`projectDescription`)
    .innerHTML.trim();
  // Remove header and add textarea
  editArea = document.getElementById(`projectHeader`).innerHTML = `
    <div class="accordion" id="accordion-project">
    <div class="card">
      <div class="card-header" id="headingOne-project">
        <h2 class="mb-0">
          <button class="btn btn-info btn-block text-left" type="button" data-toggle="collapse"
          data-target="#collapseOne-project" aria-expanded="true" aria-controls="collapseOne-project">
            Change Project Name
          </button>
        </h2>
      </div>
      <div id="collapseOne-project" class="collapse show" aria-labelledby="headingOne-project" data-parent="#accordion-project">
        <div class="card-body">
            <form id="editProjectNameForm">
                <label for="projectName">Edit project name</label>
                <textarea class="form-control" id="projectName" 
                 placeholder="Enter new project name" rows="3" maxlength="64">${projectName}</textarea>
                <div class="w-100 py-1"></div>
                <div class="container-fluid text-right col">
                  <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                  <input type="submit" class="btn btn-primary"/>
                </div>
            </form>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header" id="headingTwo-project">
        <h2 class="mb-0">
          <button class="btn btn-info btn-block text-left" type="button" data-toggle="collapse"
           data-target="#collapseTwo-project" aria-expanded="false" aria-controls="collapseTwo-project">
            Change Project Description
          </button>
        </h2>
      </div>
      <div id="collapseTwo-project" class="collapse" aria-labelledby="headingTwo-project" data-parent="#accordion-project">
        <div class="card-body">
            <form id="editProjectDescriptionForm">
                <label for="projectDescription">Edit project description</label>
                <textarea class="form-control" id="projectDescription" 
                 placeholder="Enter new project description" rows="6" maxlength="1024">${projectDescription}</textarea>
                <div class="w-100 py-1"></div>
                <div class="container-fluid text-right col">
                  <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                  <input type="submit" class="btn btn-primary"/>
                </div>
            </form>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header" id="headingThree-project">
        <h2 class="mb-0">
          <button class="btn btn-info btn-block text-left collapsed" type="button" data-toggle="collapse"
          data-target="#collapseThree-project" aria-expanded="false" aria-controls="collapseThree-project">
            ${
              image
                ? "Alter Project Image Banner"
                : "Upload Project Image Banner"
            }
          </button>
        </h2>
      </div>
      <div id="collapseThree-project" class="collapse" aria-labelledby="headingThree-project" data-parent="#accordion-project">
        <div class="card-body">
            <form id="projectImageBannerEditForm" action="/edit/file/${projID}/"
            enctype="multipart/form-data" method="POST">
              <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
              <input type="hidden" name="type" value="${type}">
              <input type="hidden" name="modify" value="modify">
              <div class="container-fluid row">
                  <div class="container-fluid col-1 align-self-end">
                    <button id="clearProjectBanner" class="btn btn-secondary btn-sm" type="button" disabled
                    onclick="document.getElementById('uploadedProjectBanner').value = '';
                    document.getElementById('clearProjectBanner').disabled = true;">Clear File</button>
                  </div>
                  <div class="container-fluid col-11">
                    ${
                      image
                        ? // if image banner exists, offer to change
                          `<label for="uploadedProjectBanner">Change Project Image Banner</label>
                          <input type="file" id="uploadedProjectBanner" name="uploadedFile" 
                            accept="image/*" class="form-control">`
                        : // no project image banner, offer to upload
                          `<label for="uploadProjectBanner">Add New Project Image Banner</label>
                          <input type="file" id="uploadProjectBanner" name="uploadedFile" 
                            accept="image/*" class="form-control">`
                    }
                  </div>
              </div>
              <div class="w-100 py-1"></div>
              <div class="container row">
                <div class="container-fluid text-left col">
                  ${
                    image
                      ? // if image, remove image
                        `<label for="removeProjectBanner">Or</label>
                        <button class="btn btn-danger" type="button" id="removeProjectBanner"
                        onclick="removeAnnex('projectBanner', ${projID})">
                        Remove Current Image</button>`
                      : ""
                  }
                </div>
                <div class="container-fluid text-right col">
                  <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                  <input type="submit" class="btn btn-primary"/>
                </div>
              </div>
            </form>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header" id="headingFour-project">
        <h2 class="mb-0">
          <button class="btn btn-info btn-block text-left" type="button" data-toggle="collapse"
          data-target="#collapseFour-project" aria-expanded="false" aria-controls="collapseFour-project">
            ${isProjArchived ? "Un-Archive" : "Archive"} Project
          </button>
        </h2>
      </div>
      <div id="collapseFour-project" class="collapse" aria-labelledby="headingFour-project" data-parent="#accordion-project">
        <div class="card-body">
            <form id="archiveProjectForm">
              <label for="archiveProject">Do you wish to ${isProjArchived ? "" : "un"}archive this project?</label>
              ${isProjArchived 
                ?
                `<button class="btn btn-primary" type="button" id="archiveProject" onclick="setProjectArchive(false)">
                  Yes, make this Project active again
                </button>`
                :
                `<button class="btn btn-danger" type="button" id="archiveProject" onclick="setProjectArchive(true)">
                  Yes, archive this Project
                </button>`
              }
              
                <div class="w-100 py-1"></div>
                <div class="container-fluid text-right col">
                  <button class="btn btn-secondary" type="button" onclick="reloadPage()">Cancel</button>
                </div>
            </form>
        </div>
      </div>
    </div>
  </div>
  <div class="w-100 py-2"></div>`;

  // See if image banner was presented for upload
  seeIfBannerPresent = document.querySelector(
    `#upload${image ? `ed` : ""}ProjectBanner`
  ).value;
  if (!seeIfBannerPresent) {
    // No file present, upload just text
    document.querySelector(`#editProjectNameForm`).onsubmit = () => {
      // Get text from textarea
      let name = document.querySelector(`#projectName`).value.trim();
      if (name !== projectName) {
        // Pass text to Poster handler
        updatePostText("projectName", name, projID);
      }
      return false;
    };
    document.querySelector(`#editProjectDescriptionForm`).onsubmit = () => {
      // Get text from textarea
      let description = document
        .querySelector(`#projectDescription`)
        .value.trim();
      if (description !== projectDescription) {
        // Pass text to Poster handler
        updatePostText("projectDescription", description, projID);
      }
      return false;
    };
  }

  document
    .querySelector(`#upload${image ? `ed` : ""}ProjectBanner`)
    .addEventListener("change", () => {
      // Get text from textarea
      var innit = document.getElementById(
        `upload${image ? `ed` : ""}ProjectBanner`
      ).value;
      if (innit !== "") {
        document.getElementById(`clearProjectBanner`).disabled = false;
      }
    });
}

async function updatePostText(type, text, postID) {
  const request = new Request(`/edit/text/${postID}/`, {
    headers: { "X-CSRFToken": csrftoken },
  });

  fetch(request, {
    method: "POST",
    mode: "same-origin", // Do not send CSRF token to another domain.
    body: JSON.stringify({
      type: type,
      text: `${text}`,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.error === undefined) {
        // Print result
        alert(result.message);
        // console.log(result);
      } else {
        // console.error(result);
        alert(result.error);
      }
    })
    .then(function () {
      reloadPage();
    });
}

async function removeAnnex(type, postID) {
  types = ["commit", "commit/image", "document", "projectBanner"];
  if (!types.includes(type)) {
    alert("post type not supported");
    return Error("post type not supported");
  }
  if (type === "document") {
    if (
      !confirm("Are you sure? This will delete both the document and its text!")
    ) {
      return Error("User cancelled the deletion of file");
    }
  } else if (type === "commit") {
    if (!confirm("Are you sure? This will delete the entire commit!")) {
      return Error("User cancelled the deletion of commit");
    }
  } else if (type === "commit/image") {
    if (
      !confirm(
        "Are you sure? This will delete the image associated with this commit!"
      )
    ) {
      return Error("User cancelled the deletion of file");
    }
  } else if (type === "projectBanner") {
    if (
      !confirm(
        "Are you sure? This will delete the image banner of this project!"
      )
    ) {
      return Error("User cancelled the deletion of file");
    }
  }

  const request = new Request(`/delete/${postID}/`, {
    headers: { "X-CSRFToken": csrftoken },
  });

  fetch(request, {
    method: "POST",
    mode: "same-origin", // Do not send CSRF token to another domain.
    body: JSON.stringify({
      type: type,
      remove: "remove",
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.error === undefined) {
        // Print result
        alert(result.message);
        // console.log(result);
      } else {
        // console.error(result);
        alert(result.error);
      }
    })
    .then(reloadPage);
}

async function setProjectArchive(yayornay) {
    if (
      !confirm(
        `Are you sure? This will ${yayornay ? "" : "un"}archive this project!`
        )
      ) {
      return Error("User cancelled the project archivement operation");
    }

  const request = new Request(`/archive/${Number(getProjectID())}/`, {
    headers: { "X-CSRFToken": csrftoken },
  });

  fetch(request, {
    method: "POST",
    mode: "same-origin", // Do not send CSRF token to another domain.
    body: JSON.stringify({
      archive: `${yayornay ? "" : "un"}archive`
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.error === undefined) {
        // Print result
        // console.log(result);
        alert(result.message);
      } else {
        // console.error(result);
        alert(result.error);
      }
    })
    .then(reloadPage);
}

function reloadPage() {
  location.reload();
  return false;
}
