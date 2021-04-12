$(document).ready(function() {
   var category_line_up_form = new FormModal('category_line_up_form');
   $('document').on('click', '#category_line_up_show', function (){
      category_line_up_form.show()
   });
   $('document').on('click', '#category_line_up_submit', function (){
      $('#category_line_up_form').submit();
   });
   $('select[multiple]').select2({
      allowClear: true,
      closeOnSelect: false,
   });
});
