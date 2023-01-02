let is_hidden = true

function giveId() {
    let champions = document.getElementsByClassName("champions")
    let championsBtn= document.getElementsByClassName("champions-button")
    for (let i = 0; i < champions.length; i++) {
        champions[i].setAttribute("id", "champions-" + i)
        championsBtn[i].setAttribute("id", "champions-button-" + i)
        championsBtn[i].onclick = function() { hide(i) }
    }
}

function hide(id) {
    let champions = document.getElementById("champions-" + id)
    let championsBtn = document.getElementById("champions-button-" + id)
    if (is_hidden) {
        championsBtn.innerText = "Hide champions"
        champions.style.display = "flex"
    } else {
        championsBtn.innerText = "Show champions"
        champions.style.display = "none"
    }
    is_hidden = !is_hidden
}

giveId()