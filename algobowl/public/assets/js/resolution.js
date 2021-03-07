// -*- mode: js; js-indent-level: 2; -*-
(function ($) {
  $('.upload-new').click(function (ev) {
    ev.preventDefault();
    var output_id = $(this).data('output');

    $('#file-upload-' + output_id).trigger('click');
  });

  var statusfunc = function (data) {
    if (data['status'] == 'success') {
      window.location.reload();
    }
    else {
      window.alert(data['msg']);
    }
  };

  var confirm_file = null;
  var confirm_to_group = null;
  var base_url = window.location.href;

  if (base_url.includes('/stage/')) {
    base_url += '/../..';
  }

  $('.hidden-uploader').on('change', function (ev) {
    ev.preventDefault();
    confirm_to_group = $(this).data('togroup');
    confirm_file = this.files[0];

    $('#upload-warning-modal').modal();
  });

  $('#upload-anyway').on('click', function (ev) {
    var formdata = new FormData();
    formdata.append('output_file', confirm_file);

    $.ajax({
      url: base_url + '/submit_output/' + confirm_to_group,
      method: 'POST',
      data: formdata,
      success: statusfunc,
      error: function () {
        statusfunc({
          status: 'err',
          'msg': 'Unknown error. Try refreshing the page.'});
      },
      dataType: 'json',
      contentType: false,
      processData: false});
  });

  $('.protest').click(function (ev) {
    ev.preventDefault();
    var output_id = $(this).data('output');
    console.log(output_id);

    $.get(
      base_url + '/resolution_protest/' + output_id,
      {},
      statusfunc,
      'json');
  });
})(jQuery);
