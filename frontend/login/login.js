// static/login/login.js
import { saveToken } from "/js/auth.js";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#login-form");
  const usernameInput = document.querySelector("#username");
  const passwordInput = document.querySelector("#password");
  const failedLoginMessage = document.getElementById("failed-login");
  const box = document.querySelector("#login-container");
  const title = document.querySelector(".title");

  title.addEventListener("click", function () {
    window.location.href = "/";
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    login(usernameInput.value.trim(), passwordInput.value);
  });

  function triggerShake(element) {
    element.classList.add("shake");
    setTimeout(() => element.classList.remove("shake"), 400);
  }

  async function login(username, password) {
    failedLoginMessage.style.display = "none";

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        failedLoginMessage.textContent = data.error || "Login failed";
        failedLoginMessage.style.display = "block";
        triggerShake(box);
        return;
      }

      saveToken(data.token);

      window.location.replace('/dashboard/');

    } catch (err) {
      failedLoginMessage.textContent = "Network error. Please try again.";
      failedLoginMessage.style.display = "block";
      triggerShake(box);
    }
  }

  document.getElementById("register").addEventListener("click", function () {
    window.location.href = "/register/";
  });
});
