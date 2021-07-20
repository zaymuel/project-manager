/* Prevents user from changing project in commit creation screen */
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
