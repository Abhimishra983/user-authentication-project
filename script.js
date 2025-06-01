function showLogin() {
  document.getElementById("loginForm").classList.add("active");
  document.getElementById("registerForm").classList.remove("active");
}

function showRegister() {
  document.getElementById("registerForm").classList.add("active");
  document.getElementById("loginForm").classList.remove("active");
}

function toggleTheme() {
  const body = document.body;
  const isDark = body.classList.contains("dark-theme");

  body.classList.toggle("dark-theme", !isDark);
  body.classList.toggle("light-theme", isDark);
  localStorage.setItem("theme", isDark ? "light" : "dark");
}

window.onload = function () {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add(`${savedTheme}-theme`);
  document.getElementById("themeSwitch").checked = savedTheme === "dark";

  setupPasswordToggle("showLoginPassword", "loginPassword");
  setupPasswordToggle("showRegisterPassword", "registerPassword");
};

function setupPasswordToggle(checkboxId, passwordInputId) {
  const checkbox = document.getElementById(checkboxId);
  const passwordInput = document.getElementById(passwordInputId);

  if (checkbox && passwordInput) {
    checkbox.addEventListener("change", function () {
      passwordInput.type = this.checked ? "text" : "password";
    });
  }
}

function anyFieldEmpty(fields) {
  return fields.some(field => !field.trim());
}

function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

async function registerUser(username, email, password) {
  const res = await fetch("http://localhost:8080/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
    credentials: "include",
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

async function loginUser(email, password) {
  const res = await fetch("http://localhost:8080/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

document.getElementById("registerFormElement").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username = document.getElementById("registerUsername").value;
  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;

  if (anyFieldEmpty([username, email, password])) {
    alert("Please fill all fields");
    return;
  }

  if (!isValidEmail(email)) {
    alert("Please enter a valid email address");
    return;
  }

  if (username.trim().toLowerCase() === email.trim().toLowerCase()) {
    alert("Username should not be the same as email");
    return;
  }

  if (!/^[A-Z]/.test(password)) {
    alert("Password must start with a capital letter");
    return;
  }

  if (!/\d/.test(password)) {
    alert("Password must contain at least one number");
    return;
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    alert("Password must include at least one special character");
    return;
  }

  try {
    const { ok, data } = await registerUser(username, email, password);
    if (ok && data.success) {
      alert("Registration successful!");
      window.location.href = "home.html";
    } else {
      alert("Error: " + (data.message || "Unknown error"));
    }
  } catch {
    alert("Server error!");
  }
});

document.getElementById("loginFormElement").addEventListener("submit", async function (e) {
  e.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  if (anyFieldEmpty([email, password])) {
    alert("Please enter both email and password");
    return;
  }

  if (!isValidEmail(email)) {
    alert("Please enter a valid email address");
    return;
  }

  try {
    const { ok, data } = await loginUser(email, password);
    if (ok && data.success) {
      alert("Login successful!");
      window.location.href = "home.html";
    } else {
      alert("Login failed: " + (data.message || "Unknown error"));
    }
  } catch {
    alert("Server error!");
  }
});

// === Forgot Password Logic ===

function showForgotPassword() {
  document.getElementById("forgotDiv").style.display = "block";
}

function resetPassword() {
  const username = document.getElementById("fp-username").value;
  const newPassword = document.getElementById("fp-newpass").value;

  if (!username.trim() || !newPassword.trim()) {
    alert("Please enter both username and new password.");
    return;
  }

  fetch("http://localhost:3000/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, newPassword }),
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      document.getElementById("forgotDiv").style.display = "none";
    })
    .catch(() => {
      alert("Server error!");
    });
}
