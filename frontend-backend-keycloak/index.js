//python -m http.server 3000

const KEYCLOAK_URL = "http://localhost:8080/realms/Simple-web-App/protocol/openid-connect/auth";
const CLIENT_ID = "Simple-web-app-Keycloak";
const REDIRECT_URI = "http://localhost:3000";
const API_BASE = "http://localhost:5000/api";

function login() {
  const url =
    `${KEYCLOAK_URL}` +
    `?client_id=${CLIENT_ID}` +
    `&response_type=token` +
    `&redirect_uri=${REDIRECT_URI}`;

  window.location.href = url;
}

function logout() {
  localStorage.removeItem("token");
  updateStatus();
  const logoutUrl = `http://localhost:8080/realms/Simple-web-App/protocol/openid-connect/logout?post_logout_redirect_uri=http://localhost:3000&client_id=Simple-web-app-Keycloak`;
  window.location.href = logoutUrl;
  setOutput("Logout effettuato");
}


function handleCallback() {
  if (window.location.hash) {
    const params = new URLSearchParams(window.location.hash.substring(1));
    const token = params.get("access_token");

    if (token) {
      localStorage.setItem("token", token);
      window.location.hash = "";
    }
  }
}

async function callApi(endpoint) {
  const token = localStorage.getItem("token");
  console.log(token);

  if (!token) {
    setOutput("Non sei autenticato");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
      }
    });

    const data = await res.json();

    setOutput(JSON.stringify(data, null, 2));

  } catch (err) {
    setOutput("Errore chiamata API");
  }
}


function getUser() {
  callApi("/user");
}


function getAdmin() {
  callApi("/admin");
}

function setOutput(text) {
  document.getElementById("output").innerText = text;
}

function updateStatus() {
  const token = localStorage.getItem("token");
  const status = document.getElementById("status");

  if (token) {
    status.innerText = "Stato: autenticato";
  } else {
    status.innerText = "Stato: non autenticato";
  }
}


document.getElementById("loginBtn").addEventListener("click", login);
document.getElementById("logoutBtn").addEventListener("click", logout);
document.getElementById("userBtn").addEventListener("click", getUser);
document.getElementById("adminBtn").addEventListener("click", getAdmin);

handleCallback();
updateStatus();