function login() {
  const url =
    `${CONFIG.KEYCLOAK_URL}` +
    `?client_id=${CONFIG.CLIENT_ID}` +
    `&response_type=token` +
    `&redirect_uri=${CONFIG.REDIRECT_URI}`;

  window.location.href = url;
}

function logout() {
  localStorage.removeItem("token");
  updateStatus();
  const logoutUrl = `${CONFIG.KEYCLOAK_BASE_URL}/realms/${CONFIG.KEYCLOAK_REALM}/protocol/openid-connect/logout?post_logout_redirect_uri=${CONFIG.REDIRECT_URI}&client_id=${CONFIG.CLIENT_ID}`;
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

async function callApi(endpoint, port) {
  const token = localStorage.getItem("token");
  if (!token) {
    setOutput("Non sei autenticato");
    return;
  }

  try {
    const res = await fetch(`http://localhost:${port}/api${endpoint}`, {
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
      }
    });

    const data = await res.json();

    return data;

  } catch (err) {
    return "API error";
  }
}

async function getAdmin() {
  const data = await callApi("/admin", CONFIG.ADMIN_SERVICE_PORT);
  setOutput(JSON.stringify(data, null, 2));
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
document.getElementById("getPosts").addEventListener("click", () => {
  window.location.href = "./posts.html";
});
document.getElementById("adminBtn").addEventListener("click", getAdmin);

document.getElementById("postForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    if (!token) {
      setOutput("Non sei autenticato");
      return;
    }

    try {
      const data = {
        title: document.querySelector("[name=title]").value,
        content: document.querySelector("[name=content]").value
      };

      const res = await fetch("http://localhost:5001/api/createPost", {
          method: "POST",
          headers: {
              "Authorization": "Bearer " + token,
              "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
      });

      const result = await res.json();
      setOutput(JSON.stringify(result, null, 2));
    }
    catch(err) {
      setOutput("API error");
    }
});

handleCallback();
updateStatus();