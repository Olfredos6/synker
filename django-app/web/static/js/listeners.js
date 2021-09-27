/** Elements' event listeners */

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
        inview_repo = data
        document.querySelector("#repo-about").innerHTML = repoAboutComponent(data.repo)
        document.getElementById('tree').innerHTML = ""
        var tree = new Tree(document.getElementById('tree'));
        tree.json(structPrepareTreeJS(data.struct))

        // for apps that live in the main dir
        render(`${PHP_SERVER}/${inview_repo.repo.id}`)
    })
    
})

$("#tree").on("click", "summary[class=selected]", e => {
    // @TODO: Debounce
    const pathToDir = rebuildDirPath(e.target)
    render(`${PHP_SERVER}/${inview_repo.repo.id}/${pathToDir}`)
})


document.querySelector("#btn-code-tab").addEventListener("click", ()=>{
    // starts live code-server on the current repo
    requestCodeServer(inview_repo.repo.id)
    .then(data => {
        if(!data){ alert("Code-server failed to start") }
        else{
            showSourceCode(data.port)
        }
    })
})


document.querySelector("#nav-tab").addEventListener("cick", (e)=>{
    /**
     * after 5 minutes of not activating the source-code tab,
     * sends a request to kill the container running the repo's
     * code-server.
     */
    
})