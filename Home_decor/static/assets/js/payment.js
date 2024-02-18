
async function updateOrderSummary() {
    try {
        const response = await fetch('/order-summary/');
        const data = await response.json();
        document.getElementById('total').innerText = `$${data.total}`;
        document.getElementById('quantity').innerText = `Subtotal (${data.quantity} items)`;
        document.getElementById('shipping').innerText = `$${data.shipping}`;
        document.getElementById('before_tax').innerText = `$${parseInt(data.shipping) + parseInt(data.total)}`;
        document.getElementById('tax').innerText = `$${data.tax}`;
        document.getElementById('discount').innerText = `$${data.discount_amount}`;
        document.getElementById('grandtotal').innerText = `$${data.grandtotal}`;
    } catch (error) {
        console.error('Error fetching order summary:', error);
    }
}

updateOrderSummary();

function default_address(addressId) {
    fetch('/myaccount/my-address/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Include CSRF token
        },
        body: JSON.stringify({ 'addressId': addressId }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                Swal.fire('Success', data.message, 'success');
            } else {
                Swal.fire('Error', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire('Error', 'An unexpected error occurred', 'error');
        });

}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if the cookie name matches the provided name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

const csrftoken = getCookie('csrftoken');




document.getElementById('rzp-button1').onclick = function (e) {
    // Check if the Razorpay payment method is selected
    var selectedPaymentMethod = document.querySelector('input[name="payment_method"]:checked');
    console.log(selectedPaymentMethod.value, 'as');

    if (selectedPaymentMethod.value == 2) {


        // Create the fetch request
        fetch('/payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                // Add any additional headers if needed
            },
            body: JSON.stringify({
                selected_payment_method: selectedPaymentMethod.value
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Parse response JSON
            })
            .then(data => {
                e.preventDefault();
                const paymentOrderId = data.context.id;
                const paymentAmount = data.context.amount
                var razorpayKeyId = '{{ RAZOR_PAY_KEY_ID }}';
                var callbackURL = `http://127.0.0.1:8000/paymenthander/`;
                var options = {
                    "key": razorpayKeyId,
                    "amount": paymentAmount,
                    "name": "Home Decor",
                    "description": "Test Transaction",
                    "image": "https://example.com/your_logo",
                    "order_id": paymentOrderId, //This is a sample Order ID. Pass the `id` obtained in the response of Step 1

                    "callback_url": callbackURL,


                    "prefill": {
                        "name": "{{request.user.get_usernme}}",
                        "email": "{{request.user.email}}",
                        "contact": "{{request.user.phone_number}}"
                    },
                    "theme": {
                        "color": "#b19361"
                    }
                };
                var rzp1 = new Razorpay(options);
                rzp1.on('payment.failed', function (response) {
                    alert(response.error.code);
                });

                rzp1.open();
                e.preventDefault();

            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });

    }

    else {
        e.preventDefault();

        fetch('/payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                selected_payment_method: selectedPaymentMethod.value
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                e.preventDefault();
                console.log('Payment successful:', data);
                window.location.href = 'http://127.0.0.1:8000/order-review/';
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }
};
