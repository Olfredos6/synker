/** UI handling */

function showSearchResults(results) {
    let html = ""
    if (results == []) { html = "<p>No repository found.</p>" }
    else {
        results.forEach(repo => {
            html += `<li class="list-group-item">${repo.name}</li>`
        });
    }
    document.querySelector("#search-result").innerHTML = html
}