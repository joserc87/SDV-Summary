function flashed_close(id) {
	$(document.getElementById(id)).slideUp(400);
}

$(document).ready(function() {
	$(".clickable").click(function() {
		var splitstr = $(this).attr('id').split('-')
		if ( splitstr[1] == 'scafc' ) {
			var now = new Date();
			var time = now.getTime();
			var expireTime = time + 30000*36000;
			now.setTime(expireTime);
			document.cookie = splitstr[2]+'=true;expires='+now.toGMTString()+';path=/';
			flashed_close(splitstr[0]+'-container');
		}
		else if ( splitstr[1] == 'fc' ) {
			flashed_close(splitstr[0]+'-container');
		}
		else {
		};
	});
});