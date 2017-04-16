/*

insights.js displays/hides the insights tab on profiles

*/
function insight_close() {
	$(document.getElementById('insight')).slideUp(400);
}

function insight_open() {
	$(document.getElementById('insight')).slideDown(400);
	//$(document).scrollTop($('#insight').offset().top);
	$('html, body').animate({scrollTop: $('#insight').offset().top}, 400);
}

var insight_state = false;

function insight_setup() {
	if (insight_state != false) {
		$(document.getElementById('insight')).show();
	} 
}

function set_insight_bindings() {
	$("#insight-show").click(function() {
		insight_state = true;
		insight_open();
		$('button').tooltip('hide');
	});	
	$("#insight-hide").click(function() {
		insight_state = false;
		insight_close();
		$('button').tooltip('hide');
	});	
}

function set_insight_buttons() {
	if (insight_state != false) {
		$(document.getElementById('insight-show')).hide();
		$(document.getElementById('insight-hide')).show();
	} else {
		$(document.getElementById('insight-hide')).hide();
		$(document.getElementById('insight-show')).show();
	}
}

$(document).ready(function() {
	insight_setup();
	set_insight_buttons();
	set_insight_bindings();
	$('#insight-button').on('shown.bs.tooltip', function() {
		set_insight_buttons();
		set_insight_bindings();
	});
});


