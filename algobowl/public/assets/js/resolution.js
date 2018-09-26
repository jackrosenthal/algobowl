(function ($) {
  $('.upload-new').click(function (ev) {
    ev.preventDefault();
    var output_id = $(ev.target).data('output');

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

  $('.hidden-uploader').on('change', function (ev) {
    ev.preventDefault();
    var to_group = $(ev.target).data('togroup');

    var formdata = new FormData();
    formdata.append('output_file', ev.target.files[0]);


    $.ajax({
      url: window.location.href + '/submit_output/' + to_group,
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
    var output_id = $(ev.target).data('output');
    console.log(output_id);

    $.get(
      window.location.href + '/resolution_protest/' + output_id,
      {},
      statusfunc,
      'json');
  });
})(jQuery);
