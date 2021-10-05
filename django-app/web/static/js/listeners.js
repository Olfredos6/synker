/** Elements' event listeners */

document.querySelector("#txt-search").addEventListener("input", (e) => {
    let keyword = e.target.value

    if (keyword !== "") {

        if(keyword.length > 3) {
            resultListElement.innerHTML = spinnerComponent("searching...")    
            searchRepo(e.target.value).then(results => showSearchResults(results))
        }
    } else {
        // make sure to hide it
        resultListElement.innerHTML = "<p>No repo found</p>"
    }
})

document.querySelector(".btn-refresh-iframe").addEventListener('click', (e) => {
    render(renderer.src, true)
})

$("body").on("click", ".repo-list-item", (e) => {
    /**
     * Triggered when a repo item is clicked from the repo search result
     * Get and displays repo data, structure
     */
    resultListElement.innerHTML = ""
    document.getElementById('tree').innerHTML = spinnerComponent()
    getRepository(e.target.dataset.id).then(data => { displayRepo(data) })
})

document.querySelector("#txt-search").addEventListener('click', () => {
    // check if the repo in view was edited and notify before leaving
    if (inview_repo) {
        checkInViewRepoWasEdited()
            .then(status => REPO_WAS_EDITED = status)
    }
    else
        REPO_WAS_EDITED = 999
})

$("#tree").on("click", "summary[class=selected]", e => {
    // @TODO: Debounce
    const pathToDir = rebuildDirPath(e.target)
    render(`${PHP_SERVER}/${inview_repo.repo.id}/${pathToDir}`)
})


document.querySelector("#btn-code-tab").addEventListener("click", () => {
    // starts live code-server on the current repo
    if (inview_repo) requestCodeServer(inview_repo.repo.id)
        .then(data => {
            if (!data) {
                killCodeServer(inview_repo.repo.id)
                killCodeServerView()
                alert("Code-server failed to start")
                BTN_TAB_CODE.classList.remove("disabled")
            }
            else {
                showSourceCode(data.port)
            }
        })
})

let kill_code_server_timeout = null
document.querySelector("#nav-tab").addEventListener("cick", (e) => {
    /**
     * after 5 minutes of not activating the source-code tab,
     * sends a request to kill the container running the repo's
     * code-server.
     */
    if (e.target != BTN_TAB_CODE) {
        kill_code_server_timeout = setTimeout(killCodeServer, 50000)
    } else {
        clearTimeout(kill_code_server_timeout)
    }
})


document.querySelector(".btn-submit-repo-edit").addEventListener('click', () => {
    const formData = formToJSON("frm-edit-repo-st-info")
    createOrUpdateRepoStudentInfo(formData)
        .then(data => {
            if (!data) { /* Not sure what to do for now */ }
            else {

            }
        })
})


document.querySelector(".sidebar").addEventListener("change", (e) => {
    if (e.target.id == "sel-switch-branch") {
        const checkout_branch = e.target.value
        repoCheckoutBranch(inview_repo.repo.id, checkout_branch)
            .then(res => {
                if (!res.ok) { notify(`Checking out to branch ${checkout_branch} failed. ${res.responseText}`); return null }
                else return res.json()
            })
            .then(data => {
                if (data) {
                    displayRepo(data)
                }
            })
    }
})