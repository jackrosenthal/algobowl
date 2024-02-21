(function ($) {
  $(function () {
    /* Enable tooltips */
    $('[data-toggle="tooltip"]').tooltip()

    /* Show times in browser local timezone */
    $('time').replaceWith(function () {
      const date = new Date($(this).attr("datetime"));
      return date.toLocaleString();
    });

    async function make_zip_blob(path_url_map) {
      const zip_writer = new zip.ZipWriter(
        new zip.BlobWriter("application/zip"));
      await Promise.all(Object.keys(path_url_map).map(
        (key) => zip_writer.add(key, new zip.HttpReader(path_url_map[key]))
      ));
      return zip_writer.close();
    }

    function download_zip() {
      const button = $("#zip-button");
      const links = $("[data-zip-path]");
      const button_clone = button.clone();

      button.replaceWith(
        '<div id="zip-spinner" class="spinner-border text-primary" role="status">' +
          '<span class="sr-only">Preparing ZIP...</span>' +
          '</div>');

      let path_url_map = {};
      links.each((i, link) =>
        path_url_map[$(link).attr("data-zip-path")] = $(link).attr("href"));

      make_zip_blob(path_url_map).then(function (blob) {
        button_clone.attr("href", URL.createObjectURL(blob));
        button_clone.attr("id", "zip-ready");
        $("#zip-spinner").replaceWith(button_clone);
        $("#zip-ready").get(0).dispatchEvent(
          new MouseEvent(
            "click",
            {bubbles: true, cancelable: true, view: window}));
      });
    }

    $("#zip-button").on("click", download_zip);
  });
})(jQuery);
