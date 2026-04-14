function login() {
  const url = "https://auth.local/oauth2/sign_in?rd=https://app.local";
  window.location.href = url;
}

function logout() {
  const logoutUrl = `https://auth.local/oauth2/sign_out`;
  window.location.href = logoutUrl;
  setOutput("Logout effettuato");
}

async function callApi(endpoint) {
  try {
    const res = await fetch(`https://api.local/${endpoint}`, {
      credentials: 'include'
    });

    const data = await res.json();

    return data;

  } catch (err) {
    return "API error";
  }
}

async function getAdmin() {
  const data = await callApi("/admin");
  setOutput(JSON.stringify(data, null, 2));
}

function setOutput(text) {
  document.getElementById("output").innerText = text;
}

document.getElementById("loginBtn").addEventListener("click", login);
document.getElementById("logoutBtn").addEventListener("click", logout);
document.getElementById("getPosts").addEventListener("click", () => {
  window.location.href = "./posts.html";
});
document.getElementById("adminBtn").addEventListener("click", getAdmin);

document.getElementById("postForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const data = {
        title: document.querySelector("[name=title]").value,
        content: document.querySelector("[name=content]").value
      };

      const res = await fetch("https://api.local/user/createPost", {
          method: "POST",
          credentials: 'include',
          headers: {
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