document.addEventListener("DOMContentLoaded", function(event) {
	var homelinkelement = document.getElementById("exitlink")
	var host = window.location.host
	var newhostlist = host.split(".")
	homelinkelement.href = "//" + newhostlist.slice(1).join(".")
})
