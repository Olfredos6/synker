/** Elements' event listeners */
const resultListElement = document.querySelector("#search-result")
let temp_in_view_structure

document.querySelector("#txt-search").addEventListener("input", (e) => {
    let keyword = e.target.value
    
    if (keyword !== "") {
        resultListElement.innerHTML = spinnerComponent("searching...")

        searchRepo(e.target.value).then(results => showSearchResults(results))
    } else {
        // make sure to hide it
        resultListElement.innerHTML = ""
    }
})

$("body").on("click", ".repo-list-item", (e)=>{
    /**
     * Triggered when a repo item is clicked from the repo search result
     * Get and displays repo data, structure
     */
    resultListElement.innerHTML = ""
    document.getElementById('tree').innerHTML = spinnerComponent()
    getRepository(e.target.dataset.id)
    .then( data => {
        // top, display repo name, user, and last updated time
        document.querySelector("#repo-about").innerHTML = repoAboutComponent(data.repo)
        document.getElementById('tree').innerHTML = ""
        var tree = new Tree(document.getElementById('tree'));
        tree.json(structPrepareTreeJS(data.struct))
    })
    
})

$("#tree").on("click", "summary[class=selected]", e => {
    // @TODO: Debounce
    const pathToDir = rebuildDirPath(e.target)
    console.log(pathToDir)
})