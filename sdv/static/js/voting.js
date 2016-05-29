/*
Include in any page that needs voting!

In <script> tags in source html, include:
	var votestate = {{vote|safe}}; This sets the vote state; should be a json dictionary of url:get_votes(url)

Also required for theme:
	var upvotecontents = '{{url_for('static',filename='css/voting/upvote.png')}}'; 
	var downvotecontents = '{{url_for('static',filename='css/voting/downvote.png')}}';
	var unupvotecontents = '{{url_for('static',filename='css/voting/upvoted.png')}}';
	var undownvotecontents = '{{url_for('static',filename='css/voting/downvoted.png')}}';
	var upvotehovercontents = '{{url_for('static',filename='css/voting/upvote-hover.png')}}';
	var downvotehovercontents = '{{url_for('static',filename='css/voting/downvote-hover.png')}}';

Include this script AFTER these are set.

In the HTML, you need to include two tags (div/span) with the structure below. Best to include them in {% if logged_in() %}
to ensure they only display for users who can use them!
{% if logged_in() %}
	<div class="title-vote">
		<div class="clickable vote-ps" style="border-bottom: 0px;" id="vote-ps-{{data.url}}" data-url="{{data.url}}"></div>
		<div class="clickable vote-ng" style="border-bottom: 0px;" id="vote-ng-{{data.url}}" data-url="{{data.url}}"></div>
	</div>
{% endif %}

This should then work.
*/

var upvoteclass = 'upvoteimg';
var downvoteclass = 'downvoteimg';
var upvotestructure = '<img class="voteimg '+upvoteclass+'" title="Upvote this farm" src="">';
var downvotestructure = '<img class="voteimg '+downvoteclass+'" title="Downvote this farm" src="">';

function post_vote(type,url) {
	if (type=='ng') {
		if (votestate[url] == false) {
			var vote = null
		}
		else {
			var vote = false
		}
	}
	else if (type=='ps') {
		if (votestate[url] == true) {
			var vote = null
		}
		else {
			var vote = true
		}
	}
	$.post('/_vote',{'vote':vote, url: url},function(result) {
		if ( result != 'true') {
			window.alert(result);
		}
		else {
			votestate[url] = vote;
			toggle_vote();
		}
	});
}

function toggle_vote() {
	for (var url in votestate) {
		if (votestate[url] == null) {
				$("#vote-ps-"+url+' > .'+upvoteclass).attr("src",upvotecontents);
				$("#vote-ng-"+url+' > .'+downvoteclass).attr("src",downvotecontents);
			}
			else if (votestate[url] == true) {
				$("#vote-ps-"+url+' > .'+upvoteclass).attr("src",unupvotecontents);
				$("#vote-ng-"+url+' > .'+downvoteclass).attr("src",downvotecontents);
			}
			else if (votestate[url] == false) {
				$("#vote-ps-"+url+' > .'+upvoteclass).attr("src",upvotecontents);
				$("#vote-ng-"+url+' > .'+downvoteclass).attr("src",undownvotecontents);
		}
	}
}

function voting_setup() {
	$(".vote-ps").html(upvotestructure);
	$(".vote-ng").html(downvotestructure);
	toggle_vote();
	$(".clickable").click(function() {
		var splitstr = $(this).attr('id').split('-')
		if ( splitstr[0] == 'vote' ) {
			post_vote(splitstr[1],$(this).attr("data-url"));
		}
		else {
		};
	});	
	$(".voteimg").hover(function() {
		if ( $(this).attr("class").split(" ")[1] == "upvoteimg" ) {
			$(this).attr("src",upvotehovercontents);
		}
		else if ( $(this).attr("class").split(" ")[1] == "downvoteimg") {
			$(this).attr("src",downvotehovercontents);
		}
	},function() {
		toggle_vote()
	});
}

$(document).ready(function() {
	voting_setup();
});