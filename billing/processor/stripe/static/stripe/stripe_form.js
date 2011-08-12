$(document).ready(function() {
    function addInputNames() {
        // Not ideal, but jQuery's validate plugin requires fields to have names
        // so we add them at the last possible minute, in case any javascript 
        // exceptions have caused other parts of the script to fail.
        $(".card-number").attr("name", "card-number")
        $(".card-cvc").attr("name", "card-cvc")
        $(".card-expiry-year").attr("name", "card-expiry-year")
    }

    function removeInputNames() {
        $(".card-number").removeAttr("name")
        $(".card-cvc").removeAttr("name")
        $(".card-expiry-year").removeAttr("name")
    }

    function submit(form) {
        // remove the input field names for security
        // we do this *before* anything else which might throw an exception
        removeInputNames(); // THIS IS IMPORTANT!

        // given a valid form, submit the payment details to stripe
        submit_buttons = $(form).find(':submit')
        $(submit_buttons).attr("disabled", "disabled")

        var card = {
            number: $('.card-number').val(),
            cvc: $('.card-cvc').val(),
            exp_month: $('.card-expiry-month').val(), 
            exp_year: $('.card-expiry-year').val()
        };
        if ($('.card-name').val()){
            card['name'] = $('.card-name').val();
        }
        Stripe.createToken(card, 100, function(status, response) {
            if (response.error) {
                // re-enable the submit button
                $(submit_buttons).removeAttr("disabled")

                // show the error
                $(".payment-errors").html(response.error.message);

                // we add these names back in so we can revalidate properly
                addInputNames();
            } else {
                // token contains id, last4, and card type
                var token = response['id'];

                // insert the stripe token
                var input = $('.stripe-token');
                input.attr('value', token);

                // and submit
                form.submit();
            }
        });
        
        return false;
    }
    
    // add custom rules for credit card validating
    jQuery.validator.addMethod("cardNumber", Stripe.validateCardNumber, "Please enter a valid card number");
    jQuery.validator.addMethod("cardCVC", Stripe.validateCVC, "Please enter a valid security code");
    jQuery.validator.addMethod("cardExpiry", function() {
        return Stripe.validateExpiry($(".card-expiry-month").val(), 
                                     $(".card-expiry-year").val())
    }, "Please enter a valid expiration");

    // We use the jQuery validate plugin to validate required params on submit
    $(".billing-stripe-form").validate({
        submitHandler: submit,
        rules: {
            "card-cvc" : {
                cardCVC: true,
                required: true
            },
            "card-number" : {
                cardNumber: true,
                required: true
            },
            "card-expiry-year" : "cardExpiry" // we don't validate month separately
        }
    });

    // adding the input field names is the last step, in case an earlier step errors                
    addInputNames();
});
