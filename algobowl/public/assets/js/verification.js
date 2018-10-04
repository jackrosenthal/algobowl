(function ($) {
  var update_verification_data = function (data) {
    if (data['status'] == 'error') {
      window.alert(data['msg']);
      return;
    }
    for (output_id of Object.keys(data['data'])) {
      var verif_status = data['data'][output_id];
      var accepted_button = $('#accepted-button-' + output_id);
      var rejected_button = $('#rejected-button-' + output_id);
      switch (verif_status) {
        case 'waiting':
          accepted_button.prop('disabled', false);
          rejected_button.prop('disabled', false);
          break;
        case 'accepted':
          accepted_button.prop('disabled', true);
          rejected_button.prop('disabled', false);
          break;
        case 'rejected':
          accepted_button.prop('disabled', false);
          rejected_button.prop('disabled', true);
          break;
      }
    }
  }

  $('.submit-verif').click(function (ev) {
    ev.preventDefault();
    var output_id = $(this).data('output');
    var verif_status = $(this).data('status');

    $.get(
      (window.location.href
        + '/submit_verification/'
        + output_id
        + '/' + verif_status),
      {},
      update_verification_data,
      'json');
  });
})(jQuery);
