/** Elements' event listeners */

document.querySelector("#txt-search").addEventListener("input", (e) => {
    let keyword = e.target.value
    let resultListElement = document.querySelector("#search-result")
    if (keyword !== "") {
        resultListElement.innerHTML = spinner("searching...")

        searchRepo(e.target.value).then(results => showSearchResults(results))
    } else {
        // make sure to hide it
        resultListElement.style.display = "none"
    }
})