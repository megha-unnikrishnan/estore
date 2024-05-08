
function signupform() {
    var valid = true;

    // Validate First Name
    var firstName = document.forms["myForm"]["firstname"].value.trim();
    if (firstName === "") {
        document.getElementById("firstname").innerHTML = "Please enter your first name";
        valid = false;
    } else {
        document.getElementById("firstname").innerHTML = "";
    }

    // Validate Last Name
    var lastName = document.forms["myForm"]["lastname"].value.trim();
    if (lastName === "") {
        document.getElementById("lastname").innerHTML = "Please enter your last name";
        valid = false;
    } else {
        document.getElementById("lastname").innerHTML = "";
    }

    // Validate Email
    var email = document.forms["myForm"]["email"].value.trim();
    var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        document.getElementById("email").innerHTML = "Please enter a valid email address";
        valid = false;
    } else {
        document.getElementById("email").innerHTML = "";
    }

    // Validate Mobile No
    var mobile = document.forms["myForm"]["mobile"].value.trim();
    var mobilePattern = /^[6789]\d{9}$/;
    if (!mobilePattern.test(mobile)) {
        document.getElementById("mobile").innerHTML = "Please enter a valid mobile number starting with 7, 8, 9, or 6";
        valid = false;
    } else {
        document.getElementById("mobile").innerHTML = "";
    }

    // Validate Password
    var password = document.forms["myForm"]["password"].value;
    if (password === "") {
        document.getElementById("password").innerHTML = "Please enter a password";
        valid = false;
    } else {
        document.getElementById("password").innerHTML = "";
    }

    // Validate Confirm Password
    var confirmPassword = document.forms["myForm"]["cpassword"].value;
    if (confirmPassword === "") {
        document.getElementById("confirmpassword").innerHTML = "Please confirm your password";
        valid = false;
    } else if (confirmPassword !== password) {
        document.getElementById("confirmpassword").innerHTML = "Passwords do not match";
        valid = false;
    } else {
        document.getElementById("confirmpassword").innerHTML = "";
    }

    // You can add more validations for other fields if needed

    return valid;
}

