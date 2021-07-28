function renderRating(){
	var all_rating = document.getElementsByTagName("rating");

	for(var x=0; x<all_rating.length; x++){	
		var stars = "";
		var current_rating = all_rating[x];

		var current_rating_value = parseFloat(current_rating.innerHTML);
		
		//in case of full stars
		for (var i=0; i<Math.floor(current_rating_value); i++) {
			stars = stars.concat("<span class='fas fa-star rating_1'></span>");
			console.log("full star");
		}
		
		//in case of half stars
		if(Number(current_rating_value) === current_rating_value && current_rating_value % 1 !== 0) { // meaning this is NOT int
			stars = stars.concat("<span class='fas fa-star-half-alt rating_half'></span>");
			current_rating_value++; //since one has gone
		}

		//in case of no/blank stars
		for (var i=0; i<5-current_rating_value; i++) {
			stars = stars.concat("<span class='fas fa-star rating_0'></span>");
		}
	
		current_rating.innerHTML = stars;
		console.log("updated JS");
	}
}

function drawFooter(){
	var body = document.body;
	var html = document.documentElement;

	var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
	height = height - 50;

	document.getElementsByTagName("footer")[0].style.top = height+"px";
}

renderRating();
drawFooter();