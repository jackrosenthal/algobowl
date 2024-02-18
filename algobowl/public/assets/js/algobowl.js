(function ($) {
  $(function () {
    /* Enable tooltips */
    $('[data-toggle="tooltip"]').tooltip()

    /* Show times in browser local timezone */
    $('time').replaceWith(function () {
      const date = new Date($(this).attr("datetime"));
      return date.toLocaleString();
    });
  });
})(jQuery);
