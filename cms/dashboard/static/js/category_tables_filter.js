$(document).ready(function() {
   $('select[multiple]').select2({
      allowClear: true,
      closeOnSelect: false,
      placeholder: gettext("Specs")
   });
});
