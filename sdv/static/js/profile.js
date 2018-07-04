$(document).ready(function () {
  $('.player-select-item').on('click', function (e) {
    var $this = $(e.currentTarget);
    var $openPanel = $this.closest('.info-panel');
    var $targetPanelID = $this.data('target');
    console.log($targetPanelID);
    var $targetPanel = $('#'+$targetPanelID);
    console.log($targetPanel)
    var $infoPanels = $('.info-panel');

    $openPanel.addClass('hidden');
    $targetPanel.removeClass('hidden');
  });
});