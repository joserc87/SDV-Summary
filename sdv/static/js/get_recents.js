var token = undefined;

function get_success(fulldata) {
  token = fulldata.token;
  $('#recentFarms').replaceWith(fulldata.text);
  votestate = fulldata.votes;
  voting_setup();
};

function get_recents() {
  $.ajax(
      '/_full_recents',
      {
        data: { token: token },
        statusCode: {
          202: function () {
          },
          200: get_success,
        },
      },
  );
}

$(document).ready(function () {
  setInterval(get_recents, 3000);
});