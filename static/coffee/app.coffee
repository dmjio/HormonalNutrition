$(document).ready ->
        $('.stripe-button-el').attr('disabled','disabled')
        val = false               
        $('#email').change ->
                $.ajax
                  url: "/validate/"
                  type: "GET"
                  success: (e) ->
                        if e.success
                                re = /[^\s@]+@[^\s@]+\.[^\s@]+/;
                                if re.test($('#email').val())
                                        $('.stripe-button-el').removeAttr('disabled')
                                        $('#validation').text('Success').css('color','green')
                                        return
                                else
                                        $('#validation').text("Invalid Email, Try Again").css('color','red')
                                        $('.stripe-button-el').attr('disabled','disabled')
                                        return

                        else
                                $('#validation').text("Email Taken, have you already purchased this ebook?").css('color','red')
                                $('.stripe-button-el').attr('disabled','disabled')
                        return                        
                  data: $(this).val()
                  error: (e) ->
                        alert "error"
                        return
        return