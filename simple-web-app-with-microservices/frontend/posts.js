async function loadPosts() {

    const container = document.getElementById("postsContainer");
    container.innerHTML = "";

    try {
        const res = await fetch("https://api.local/user/getPosts", {
            credentials: 'include'
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