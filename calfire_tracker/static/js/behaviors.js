jQuery(document).ready(function($) {



	$(".deployed dl").each(function(){

		var myResourceValue = $(this).find("dd");
		if(myResourceValue.text() == "n/a") {
			$(this).addClass("none");
		}

	});




}); // end doc ready