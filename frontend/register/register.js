document.addEventListener("DOMContentLoaded", function () {
  const Username = document.querySelector("#username");
  const Password = document.querySelector("#password");
  const PasswordConfirmation = document.querySelector("#password_confirmation");
  const ErrorMessage = document.querySelector("#error-message");
  const SuccessMessage = document.querySelector("#success-message");
  const Form = document.querySelector("form");
  const Title = document.querySelector(".title");

  Title.addEventListener("click", function () {
    window.location.href = "/";
  });

  Form.addEventListener("submit", async function (event) {
    event.preventDefault();

    ErrorMessage.style.display = "none";
    SuccessMessage.style.display = "none";

    const payload = {
      username: Username.value.trim(),
      password: Password.value,
      password_confirmation: PasswordConfirmation.value
    };

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        ErrorMessage.textContent = data.error || "Registration failed";
        ErrorMessage.style.display = "block";
        return;
      }

      SuccessMessage.textContent = "Registration successful! Redirecting…";
      SuccessMessage.style.display = "block";

      // OPTIONAL (for now): redirect to login
      setTimeout(() => {
        window.location.href = "/login/";
      }, 1200);

    } catch (err) {
      ErrorMessage.textContent = "Network error. Please try again.";
      ErrorMessage.style.display = "block";
    }
  });
});
