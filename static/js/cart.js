   $(document).ready(function() {
                // Function to update cart item quantity and recalculate totals
                var updateCartUrl = $('#update-cart-url').data('url');

                var couponCode = $('#coupon-code-input').val();

                function updateCartItemQuantity(itemId=null, newQuantity=null,couponCode=null) {
                    // Perform AJAX request to update cart item quantity on the server
                    $.ajax({
                        type: "POST",
                        url: updateCartUrl,
                        data: {
                            item_id: itemId,
                            new_quantity: newQuantity,
                            coupon_code: couponCode,
                            csrfmiddlewaretoken: '{{ csrf_token }}'
                        },
                        success: function(response) {
                            if (response.error) {

                                $('#error-message').text(response.error);


                                   if (response.hide_quantity) {

                        $('#quantity-'+itemId).closest('.cart-item').find('.quantity-input, .quantity-plus').prop('disabled', true);
                    } else {
                        // Show quantity input and plus/minus buttons if not hidden
                        $('#quantity-'+itemId).closest('.cart-item').find('.quantity-input, .quantity-plus').prop('disabled', false);

                    }
                             }else{
                            // Update subtotal and total values in the UI based on the response

                            $('#subtotal-'+itemId).text(response.subtotal);
//                            $('#coupon-applied-msg').text("Coupon applied successfully!");
                            $('#total').text(response.total);
                            $('#offer').text(response.offer);
                            $('#shipping-cost').text(response.shipping);
                            $('#grand_total').text(response.grand_total);
                            $('#coupon').text(response.coupon_offer);
                            $('#tax').text(response.tax);
                            $('#error-message').text('');

                            if (response.coupon_applied) {
                                      $('#coupon-applied-msg').text(response.message);
                                    $('#coupon-remove').show(); // Show the button
                                } else {
                                    $('#coupon-remove').hide(); // Hide the button
                                }

                            $('#quantity-'+itemId).closest('.cart-item').find('.quantity-input, .quantity-plus').prop('disabled', false);
                        }
                        },
                        error: function(xhr, status, error) {
                             $('#coupon-applied-msg').text("Error occurred while applying coupon.");
                        }
                    });
                }

             updateCartItemQuantity();



                $('#coupon-button').click(function() {
                var couponCode = $('#coupon-code-input').val().trim();
                // Get the entered coupon code
                var row = $(this).closest('tr');
                var itemId = row.data('item-id');
                var currentQuantity = parseInt(row.find('input[type="text"]').val());


                // Update cart item quantity and recalculate totals
                updateCartItemQuantity(itemId, currentQuantity, couponCode);

                });










                // Event listener for quantity increase button
                $('.btn-plus').click(function() {
                    var row = $(this).closest('tr');
                    var itemId = row.data('item-id');
                    var currentQuantity = parseInt(row.find('input[type="text"]').val());
                    var newQuantity = currentQuantity + 1;
                    row.find('input[type="text"]').val(newQuantity);

                    // Update cart item quantity and recalculate totals
                    updateCartItemQuantity(itemId, newQuantity);
                });
                $('.cart-item input[type="text"]').on('input', function() {
                var row = $(this).closest('tr');
                var itemId = row.data('item-id');
                var newQuantity = parseInt($(this).val());
                row.find('input[type="text"]').val(newQuantity);




                updateCartItemQuantity(itemId, newQuantity,couponCode);



            });

                // Event listener for quantity decrease button
                $('.btn-minus').click(function() {
                    var row = $(this).closest('tr');
                    var itemId = row.data('item-id');
                    var currentQuantity = parseInt(row.find('input[type="text"]').val());
                    var newQuantity = currentQuantity - 1;
                    if (newQuantity < 1) {
                        newQuantity = 1;
                    }
                    row.find('input[type="text"]').val(newQuantity);

                    // Update cart item quantity and recalculate totals
                    updateCartItemQuantity(itemId, newQuantity);
                });
            });





//    function updateQuantity(itemId) {
//        var newQuantity = $('#quantity-' + itemId).val();
//        // Call your JavaScript function to update the quantity via AJAX
//        updateCartItemQuantity(itemId, newQuantity);
//    }




$(document).ready(function() {
    // Function to remove coupon from the cart
    $('#coupon-remove').click(function() {
        var removeCouponUrl = $(this).data('remove-coupon-url');
        console.log("Remove Coupon URL:", removeCouponUrl); // Check URL in console

        // Obtain CSRF token from a hidden input field
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        // Perform AJAX request to remove coupon from the cart
        $.ajax({
            type: "POST",
            url: removeCouponUrl,
            data: {
                csrfmiddlewaretoken: csrfToken
            },
            success: function(response) {
                // Handle success response, such as updating the UI
                // For example, you can reload the page or update specific elements
                location.reload(); // Reload the page to reflect the changes
            },
           error: function(xhr, status, error) {
    // Handle error, if any
    console.error("AJAX Error:", error); // Log the error to the console
    console.log("Response from server:", xhr.responseText); // Log the full response from the server
}
        });
    });
});




