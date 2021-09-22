/** Elements' event listeners */
const resultListElement = document.querySelector("#search-result")

document.querySelector("#txt-search").addEventListener("input", (e) => {
    let keyword = e.target.value
    
    if (keyword !== "") {
        resultListElement.innerHTML = spinner("searching...")

        searchRepo(e.target.value).then(results => showSearchResults(results))
    } else {
        // make sure to hide it
        resultListElement.innerHTML = ""
    }
})


$("body").on("click", ".repo-list-item", (e)=>{
    /**
     * Get nd displays repo data, structure, PHP rendering
     */
    resultListElement.innerHTML = ""
    getRepository(e.target.dataset.id)
    .then( data => {
        var tree = new Tree(document.getElementById('tree'));
        tree.json(structPrepareTreeJS(data.struct))
    })
    
})