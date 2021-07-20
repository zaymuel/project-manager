/* Presents user with progress bar upon start of file upload */
document.addEventListener("DOMContentLoaded", function () {
	const projSelection = document.getElementById("id_project");
	if (projSelection.value) {
		projSelection.disabled = true;
		// re-enables field on submit
		// just to be able to read its data
		document
			.querySelector("input[type='submit']")
			.addEventListener("click", () => (projSelection.disabled = false));
	}
});

// https://www.w3schools.com/code/tryit.asp?filename=FM69GVNGDTP7
function postFile() {
	var formdata = new FormData();

	formdata.append("file1", $("#file1")[0].files[0]);

	var request = new XMLHttpRequest();

	request.upload.addEventListener("progress", function (e) {
		var file1Size = $("#file1")[0].files[0].size;

		if (e.loaded <= file1Size) {
			var percent = Math.round((e.loaded / file1Size) * 100);
			$("#progress-bar-file1")
				.width(percent + "%")
				.html(percent + "%");
		}

		if (e.loaded == e.total) {
			$("#progress-bar-file1")
				.width(100 + "%")
				.html(100 + "%");
		}
	});

	request.open("post", "/echo/html/");
	request.timeout = 45000;
	request.send(formdata);
}

function _(el) {
	return document.getElementById(el);
}

function uploadFile() {
	var file = _("file1").files[0];
	// alert(file.name+" | "+file.size+" | "+file.type);
	var formdata = new FormData();
	formdata.append("file1", file);
	var ajax = new XMLHttpRequest();
	ajax.upload.addEventListener("progress", progressHandler, false);
	ajax.addEventListener("load", completeHandler, false);
	ajax.addEventListener("error", errorHandler, false);
	ajax.addEventListener("abort", abortHandler, false);
	ajax.open("POST", "file_upload_parser.php"); // http://www.developphp.com/video/JavaScript/File-Upload-Progress-Bar-Meter-Tutorial-Ajax-PHP
	//use file_upload_parser.php from above url
	ajax.send(formdata);
}

function progressHandler(event) {
	_("loaded_n_total").innerHTML =
		"Uploaded " + event.loaded + " bytes of " + event.total;
	var percent = (event.loaded / event.total) * 100;
	_("progressBar").value = Math.round(percent);
	_("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
	_("status").innerHTML = event.target.responseText;
	_("progressBar").value = 0; //wil clear progress bar after successful upload
}

function errorHandler(event) {
	_("status").innerHTML = "Upload Failed";
}

function abortHandler(event) {
	_("status").innerHTML = "Upload Aborted";
}
