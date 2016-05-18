function ajaxSuccess(data) {
	$('#recentFarms').empty();
	$.each(data.recents, function(index, value){
		recentTemplate(value,data.votes);
	});
	votestate = data.votes;
	voting_setup();
};

function ajaxRequest(){
	$.getJSON('/_get_recents', {}, function(data){
		ajaxSuccess(data);
	});
}

function recentTemplate(recent,votes){
	var build_string = '<div class="col-md-4 col-sm-6 text-center previewbox"> \
		<a href="'+recent[0]+'"> \
			<div class="previewimage"> \
				<img src="'+ recent[5] +'" class="img-responsive farmimgpreview"> \
				<img src="'+ recent[4] +'" class="headimg" > \
			</div> \
			<div class="previewtext"> \
				'+ recent[1] +', '+ recent[2] +' Farm <br/>  '+ recent[3] +' \
			</div> \
		</a>'
	if (recent[6]!=null) {
		build_string = build_string.concat('<div class="previewdl"> \
				<img title="This farm has a downloadable savegame available" src="static/css/dl32.png"> \
			</div>');
	}
	if (votes != null) {
		build_string = build_string.concat('<div class="previewvote"> \
				<div class="clickable vote-ps" style="border-bottom: 0px;" id="vote-ps-'+recent[0]+'" data-url="'+recent[0]+'"></div> \
				<div class="clickable vote-ng" style="border-bottom: 0px;" id="vote-ng-'+recent[0]+'" data-url="'+recent[0]+'"></div> \
			</div> \
		</div>');
	}
	$('#recentFarms').append(build_string);
}

$(document).ready(function(){
	var request = ajaxRequest;
	setInterval(ajaxRequest, 3000);
});