$(document).ready(function(){
    $('body').on('click', '.view-fullscreen', function(e){
        if($('#fullscreen-modal-content').children().length === 0){
            var selector = $(e.target).data('fullscreen-target');
            $('.' + selector).clone().appendTo('#fullscreen-modal-content');
        }
        $('#fullscreen-modal').modal();
    })
})
