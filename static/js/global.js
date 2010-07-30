var checkform = $('#check-form');
var search = $('#search');
if (checkform.length == 1) {
        checkform.submit(function() {
                if (search.val().trim().length == 0) {
                        if (!search.hasClass('error')) {
                                
                                var pos = search.offset();
                                
                                search.addClass('error');
                                search.parent().parent().append('<label for="search" class="error-msg">Please enter an e-mail address.</label>');
                                checkform.find('.error-msg').css({
                                        'top': Math.round(pos.top + search.height() + 11),
                                        'left': Math.round(pos.left)
                                }).slideDown('fast');
                        }
                        return false;
                } else {
                        search.removeClass('error');
                        checkform.find('.error-msg').remove();
                }
        });
}

$('.summary-toggle').click(function(){
        $(this).siblings('p').slideToggle();
        return false;
});

$('a.new').click(function(){
        $('#search').removeClass('error').val('');
        checkform.find('.error-msg').remove();

        $('#results').slideUp();
        return false;
});