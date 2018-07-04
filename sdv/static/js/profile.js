$(document).ready(function () {
  $('.player-select-item').on('click', function (e) {
    var $this = $(e.currentTarget),
        targetID = '#' + $this.data('target');

    $this.closest('.info-panel').addClass('hidden');
    $(targetID).removeClass('hidden');
  });
});