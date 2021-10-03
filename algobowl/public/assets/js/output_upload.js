(function ($) {
  $('.output-upload-control').on('change', function (ev) {
    var to_group = this.id.split('-').pop();
    var download_link = $('#download-link-' + to_group);
    download_link.html('<span class="text-muted">Uploading...</span>');

    var formdata = new FormData();
    formdata.append('output_file', this.files[0]);

    var statusfunc = function (data) {
      download_link.html(function (status) {
        if (status == 'success') {
          return ('<a href="' + data['url'] + '"\n'
                   + 'class="btn btn-info">\n'
                     + '<i class="fas fa-file-download fa-fw"></i>\n'
                     + 'Download Submission\n'
                   + '</a>');
        }
        else {
          return '<span class="text-danger">' + data['msg'] + '</span>';
        }
      }(data['status']))};

    var url = window.location.href;
    url = url.replace('/stage/output_upload', '');
    url += '/submit_output/' + to_group;

    $.ajax({
      url: url,
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
})(jQuery);
