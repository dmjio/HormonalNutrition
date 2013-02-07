// Generated by CoffeeScript 1.3.3
(function() {

  $(document).ready(function() {
    var val;
    $('.stripe-button-el').attr('disabled', 'disabled');
    val = false;
    $('#email').change(function() {
      return $.ajax({
        url: "/validate/",
        type: "GET",
        success: function(e) {
          var re;
          if (e.success) {
            re = /[^\s@]+@[^\s@]+\.[^\s@]+/;
            if (re.test($('#email').val())) {
              $('.stripe-button-el').removeAttr('disabled');
              $('#validation').text('Success').css('color', 'green');
              return;
            } else {
              $('#validation').text("Invalid Email, Try Again").css('color', 'red');
              $('.stripe-button-el').attr('disabled', 'disabled');
              return;
            }
          } else {
            $('#validation').text("Email Taken, have you already purchased this ebook?").css('color', 'red');
            $('.stripe-button-el').attr('disabled', 'disabled');
          }
        },
        data: $(this).val(),
        error: function(e) {
          alert("error");
        }
      });
    });
  });

}).call(this);
