function get_success(fulldata) {
	$('#recentFarms').replaceWith(fulldata.text);
	console.log('added new html...')
	votestate = fulldata.votes;
	voting_setup();
	console.log('done voting setup, complete!')
};

function get_recents(){
	$.getJSON('/_mini_recents', {}, function(data){
		console.log('requested new data...')
		if (JSON.stringify(data) != current_data) {
				console.log('data was new!')
				current_data = JSON.stringify(data);
				$.getJSON('/_full_recents', {}, function(fulldata){
					get_success(fulldata);
				});
		}
	});
}

var current_data;

$(document).ready(function(){
	$.getJSON('/_mini_recents', {}, function(data) {
			current_data = JSON.stringify(data);
	});
	setInterval(get_recents, 3000);
});