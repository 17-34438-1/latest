function searchDocAjax(hospital_id, manager=0) {
	drawFooter();

	if (doc_searchBox.value == "") {
		doctor_search_result.innerHTML = "";
		return;
	}

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("doctor_search_result").innerHTML = this.responseText;

			drawFooter();
		}
	};
	xhttp.open("GET", "/search_doc_ajax/?hospital="+hospital_id+"&manager="+manager+"&search="+doc_searchBox.value, true);
	xhttp.send();
}


function get_appointment_details_ajax(appointment_id){
	//will be implemented later

	return;
}