function listview() {
		$("#browseview").hide();
		$("#listviewbtn").hide();
		$("#browseviewbtn").show();
		$("#listviewfield").show();
		if ($(window).width() < 767) {
			$(".phoneid").addClass("vicbtn vicbtn-green");
		}
}

function browseviewbtn() {
		$("#listviewfield").hide();
		$("#browseviewbtn").hide();
		$("#listviewbtn").show();
		$("#browseview").show();
}
