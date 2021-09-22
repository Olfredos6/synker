/** UI handling */

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