function signupform() {
    var firstName = document.getElementById("firstname").value;
    var lastName = document.getElementById("lastname").value;
    var email = document.getElementById("email").value;
    var mobile = document.getElementById("mobile").value;
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("cpassword").value;

    var isValid = true;

    // First Name validation
    if (!firstName.trim()) {
        document.getElementById("firstname").innerText = "First Name is required";
        isValid = false;
    } else {
        document.getElementById("firstname").innerText = "";
    }

    // Last Name validation
    if (!lastName.trim()) {
        document.getElementById("lastname").innerText = "Last Name is required";
        isValid = false;
    } else {
        document.getElementById("lastname").innerText = "";
    }

    // Email validation
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        document.getElementById("email").innerText = "Invalid email format";
        isValid = false;
    } else {
        document.getElementById("email").innerText = "";
    }

    // Mobile validation
    var mobileRegex = /^\d{10}$/;
    if (!mobileRegex.test(mobile)) {
        document.getElementById("mobile").innerText = "Mobile number must be 10 digits";
        isValid = false;
    } else {
        document.getElementById("mobile").innerText = "";
    }

    // Password validation
    if (password.length < 6) {
        document.getElementById("password").innerText = "Password must be at least 6 characters";
        isValid = false;
    } else {
        document.getElementById("password").innerText = "";
    }

    // Confirm Password validation
    if (password !== confirmPassword) {
        document.getElementById("confirmpassword").innerText = "Passwords don't match";
        isValid = false;
    } else {
        document.getElementById("confirmpassword").innerText = "";
    }

    return isValid;
}