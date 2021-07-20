/* Compresses image on client side before uploading */
import Compressor from "./node_modules/compressorjs/dist/compressor.esm.js";

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== "") {
		const cookies = document.cookie.split(";");
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === name + "=") {
				cookieValue = decodeURIComponent(
					cookie.substring(name.length + 1)
				);
				break;
			}
		}
	}
	return cookieValue;
}
const csrftoken = getCookie("csrftoken");

document.addEventListener("DOMContentLoaded", function () {
	const initForm = document.getElementById("compose-project");
	//console.log(initForm);

	document.getElementById("submit").addEventListener("click", function (btn) {
		if (
			!document.getElementById("id_project").value ||
			!document.getElementById("id_message").value
		) {
			return;
		}
		// prevent form submission
		btn.preventDefault();
		document.getElementById("submit").disabled = true;

		let blocker = document.createElement("div");
		blocker.classList = "loadingScreen align-items-center";
		blocker.id = "loading-blocker";
		document.querySelector(".body").appendChild(blocker);

		let avisoDiv = document.createElement("div");
		avisoDiv.classList = "jumbotron";
		avisoDiv.id = "avisoDiv";
		let aviso = document.createElement("p");
		aviso.textContent = "Por favor aguarde...";
		aviso.classList = "h2";

		let spacer = document.createElement("div");
		spacer.classList = "w-100 py-2";

		let progressDiv = document.createElement("div");
		progressDiv.className = "progress";

		let progressBar = document.createElement("div");
		progressBar.id = "progress-bar";
		progressBar.classList =
			"progress-bar progress-bar-striped progress-bar-animated";
		progressBar.role = "progressbar";
		progressBar.style.width = "2%";
		progressBar.textContent = "0%";
		progressDiv.appendChild(progressBar);

		avisoDiv.appendChild(aviso);
		avisoDiv.appendChild(spacer);
		avisoDiv.appendChild(progressDiv);
		avisoDiv.appendChild(spacer);
		document.getElementById("loading-blocker").appendChild(avisoDiv);

		var progess = document.getElementById("progress-bar");

		// HTML file input, chosen by user
		//console.log(document.getElementById("id_image").files);
		let cancelBtn = document.createElement("div");
		cancelBtn.id = "cancelBtn";
		cancelBtn.classList = "btn btn-secondary";
		cancelBtn.type = "button";
		cancelBtn.textContent = "Cancelar";
		avisoDiv.appendChild(cancelBtn);

		var file = document.getElementById("id_image").files[0];

		if (!file) {
			// initialize with original form
			var formData = new FormData(initForm);
			console.log(...formData);

			// create new request
			var xhr = new XMLHttpRequest();
			xhr.open("POST", `/commit/`);
			// add CSRF token
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
			xhr.onloadstart = () => {
				console.log("started loading");
			};

			// when upload finished
			xhr.onreadystatechange = function () {
				//console.log(xhr.readyState);
				// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
				if (xhr.readyState === 4) {
					// DONE uploading, this is server's response
					const serverResponse = JSON.parse(xhr.response);
					//console.log(serverResponse);
					if (serverResponse.error) {
						alert(serverResponse.error);
						location.reload();
					} else {
						alert(serverResponse.message);
						window.location.href = serverResponse.redirectUrl;
					}
				}
			};

			xhr.send(formData);
		} else {
			// initialize with original form
			var formData = new FormData(initForm);
			console.log(...formData);
			new Compressor(file, {
				quality: 0.6,
				success(result) {
					// remove original file
					//initForm.elements["image"].files[0];
					initForm.elements["image"].value = "";

					// remove image from form
					formData.delete("image");
					// put compressed image in form
					formData.append("image", result, result.name);
					
					//console.log(...formData);

					// create new request
					var xhr = new XMLHttpRequest();
					/* TODO: handle cancellations */
					xhr.open("POST", `/commit/`);
					// add CSRF token
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
					xhr.onloadstart = () => {
						console.log("started loading");
					};

					// if cancel button pressed, cancel
					document
						.getElementById("cancelBtn")
						.addEventListener("click", () => {
							xhr.abort();
						});

					xhr.upload.addEventListener(
						"progress",
						function (evt) {
							if (evt.lengthComputable) {
								let percent = Math.round(
									(evt.loaded * 100) / evt.total
								);
								progess.style.width = `${percent}%`;
								progess.innerHTML = `${percent}%`;
								/* debugging purposes
								console.log(
									"add upload event-listener " +
										evt.loaded.toLocaleString("pt-br") +
										" / " +
										evt.total.toLocaleString("pt-br") +
										`: ${percent}%`
								);
								 */
							}
						},
						false
					);

					// when upload finished
					xhr.onreadystatechange = function () {
						//console.log(xhr.readyState);
						// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
						if (xhr.readyState === 4) {
							// DONE uploading, this is server's response
							const serverResponse = JSON.parse(xhr.response);
							//console.log(serverResponse);
							if (serverResponse.error) {
								alert(serverResponse.error);
								location.reload();
							} else {
								alert(serverResponse.message);
								window.location.href =
									serverResponse.redirectUrl;
							}
						}
					};

					xhr.send(formData);
				},
				error(err) {
					console.error(err.message);
				},
			});
		}
	});
});
