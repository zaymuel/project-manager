document.addEventListener("DOMContentLoaded", function () {
	// put event listener on input fields
	// https://stackoverflow.com/questions/6623231/remove-all-white-spaces-from-text

	document.getElementById("username").addEventListener("keyup", () => {
		// Get text from textarea
		var username = document.getElementById("username").value;
		if (username !== "") {
			document.getElementById("username").value = username.replace(
				/\s/g,
				""
			);
		}
	});

	// source: https://stackoverflow.com/questions/9142527/can-you-require-two-form-fields-to-match-with-html5
	var password = document.getElementById("password");
	var confirm_password = document.getElementById("confirmation");

	function validatePassword() {
		if (password.value != confirm_password.value) {
			confirm_password.setCustomValidity("Passwords Don't Match");
		} else {
			confirm_password.setCustomValidity("");
		}
	}

	password.onchange = validatePassword;
	confirm_password.onkeyup = validatePassword;
});

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
