/** UI handling */
const resultListElement = document.querySelector("#search-result")
const renderer = document.querySelector("#renderer")
let inview_repo = undefined
const PHP_SERVER = "http://142.93.35.195:3001"

function showSearchResults(results) {
    let html = ""
    if (results == []) { html = "<p>No repository found.</p>" }
    else {
        results.forEach(repo => {
            html += `<li class="list-group-item repo-list-item" data-id="${repo.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${repo.name}">${repo.name.length < 20 ? repo.name : repo.name.substr(0,20) + "..." }</li>`
        });
    }
    document.querySelector("#search-result").innerHTML = html
}

function displayRepoTree(struct){
    let treeContainer = document.getElementById('tree')
    treeContainer.innerText = ""
    var tree = new Tree();
    tree.json(structPrepareTreeJS(struct))
}

function render(URL){
    if(renderer.src !== URL) // we only update if the URL changes. preventing unecessary reloads
        renderer.src = URL
}

render("/stats")
