(function ($) {
  var update_preview = function () {
    var evals = {};
    $('.eval-range-slider').each(function () {
      evals[$(this).attr('name')] = parseFloat($(this).val());
    });
    var total = Object.values(evals).reduce(
      function (a, b) { return a + b; }, 0.0);
    $.each(evals, function (k, v) {
      var percent = (v / total) * 100;
      $("#pb-" + k).css('width', percent + '%');
      $("#percent-" + k).html(Math.round(percent));
    });
  };
  $('.eval-range-slider').on('change', update_preview);
  $('.eval-range-slider').on('input', update_preview);
})(jQuery);
