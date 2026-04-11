async function loadPosts() {

    const container = document.getElementById("postsContainer");
    container.innerHTML = "";
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = `${CONFIG.KEYCLOAK_URL}` +
            `?client_id=${CONFIG.CLIENT_ID}` +
            `&response_type=token` +
            `&redirect_uri=${CONFIG.REDIRECT_URI}`;
        return;
    }

    try {
        const res = await fetch("http://localhost:5001/api/getPosts", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (res.status == 401) {
            throw new Error("Authentication error");
        }

        const posts = await res.json();

        posts.forEach(post => {
            const div = document.createElement("div");
            div.classList.add("post");

            div.innerHTML = `
                <h2>${post.title}</h2>
                <p>${post.content}</p>
            `;

            container.appendChild(div);
        });

    } catch (err) {
        container.innerHTML = "<p>Errore nel caricamento dei post</p>";
        console.error(err);
    }
}

window.onload = loadPosts;