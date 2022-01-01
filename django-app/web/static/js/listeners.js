/** Elements' event listeners */

document.querySelector("#txt-search").addEventListener("input", (e) => {
    let keyword = e.target.value

    if (keyword !== "") {

        if (keyword.length > 3) {
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
     * Get and displays repo data, structure, etc..
     */
    resultListElement.innerHTML = ""
    document.getElementById('tree').innerHTML = spinnerComponent()
    getRepository(e.target.dataset.id).then(data => { displayRepo(data) })
})


document.querySelector("#repo-about").addEventListener("click", (e) => {
    if (e.target.id == "repo-reload") {
        resultListElement.innerHTML = ""
        document.getElementById('tree').innerHTML = spinnerComponent()
        getRepository(inview_repo.repo.id).then(data => { displayRepo(data) })
    }
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


document.querySelector(".sidebar").addEventListener("click", e => {
    if (Array.from(e.target.classList).indexOf("edit-repo-info") != -1) {
        FRM_EDIT_ST_DETAILS.reset()
        if (!inview_repo.repo.student.detail)
            Object.keys(inview_repo.repo.student).forEach(prop => {
                document.querySelector(`[name=${prop}]`).value = inview_repo.repo.student[prop]
            })
    }
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
            if (!data) { alert("Student details edit failed!") }
            else {
                displayRepo(data)
                document.querySelector(".btn-close-edit-modal").click()
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


document.querySelector("#k-base-frm-btn-submit").addEventListener("click", () => {
    let formData = formToJSON("k-base-frm")
    if (!formData.id) {
        delete formData.id
    }
    fetch(`/knowledge-base/${localStorage.getItem("AUTH_TOKEN")}`, {
        method: "POST",
        body: JSON.stringify(formData),
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    })
        .then(res => {
            if (res.ok) { loadKBases(); document.querySelector("[name='k-base-frm']").reset(), document.querySelector("#k-base-frm-btn-close").click() }
            else { notify(res.responseText) }
        })
})

document.querySelector("#k-base-search-key").addEventListener("input", e => {
    if (e.target.value.length > 3) {
        loadKBases(e.target.value);
    }
})

document.querySelector("#k-base-main").addEventListener("click", e =>{
    if(e.target.matches(".accordion-button")) incrementBaseViewCount( e.target.dataset.base )
    if(e.target.matches("#k-base-edit")) fillKBaseFormWith(listed_k_bases.find( base => base.pk == e.target.dataset.base ))
})