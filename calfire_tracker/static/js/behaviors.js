jQuery(document).ready(function($) {



	// Sometimes RESOURCES DEPLOYED will publish "n/a" values
	// ============================================================
	$(".deployed dl").each(function(){

		var myResourceValue = $(this).find("dd");
		if(myResourceValue.text() == "n/a") {
			$(this).addClass("none");
		}

	});



	// Sometimes we won't have any UPDATES TRACKER posts
	// ============================================================
	if ($(".tertiaries .updates").length) {
		
		if ($(".tertiaries .updates article").length) {
			// do nothing; at least one has been published
		} else {
			$(".tertiaries .updates").remove();
			$(".tertiaries").addClass("just-the-facts").removeClass("clearfix");
		}

		
	}
	





}); // end doc ready