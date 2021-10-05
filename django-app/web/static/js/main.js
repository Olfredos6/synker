/** UI handling */
const resultListElement = document.querySelector("#search-result")
const renderer = document.querySelector("#renderer")
const BTN_TAB_RENDERER = document.querySelector("#btn-renderer-tab")
const BTN_TAB_CODE = document.querySelector("#btn-code-tab")
const source_code_viewer = document.querySelector("#source-code")
const NODE_ID_DISPLAY = document.querySelector("#repo-node-display")
let inview_repo = undefined
const DEFAULT_SERVER = "http://142.93.35.195"
const PHP_SERVER = `${DEFAULT_SERVER}:3001`
let REPO_WAS_EDITED = 0
const CSRF_TOKEN = undefined

function showSearchResults(results) {
    let html = ""
    if (results.length == 0 ) { html = "<p>No repository found.</p>" }
    else {
        results.forEach(repo => {
            html += `<li class="list-group-item repo-list-item" data-id="${repo.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${repo.full_name}">${repo.full_name.length < 20 ? repo.full_name : repo.full_name.substr(0, 20) + "..."}</li>`
        });
    }
    document.querySelector("#search-result").innerHTML = html
}

function displayRepo(repo_data){
    // top, display repo name, user, and last updated time
    inview_repo = repo_data
        
    NODE_ID_DISPLAY.innerText = inview_repo.repo.id
    document.querySelector("#repo-about").innerHTML = repoAboutComponent(inview_repo.repo) + repoBranchManagamentComponent(inview_repo.repo)
    document.getElementById('tree').innerHTML = ""
    var tree = new Tree(document.getElementById('tree'));
    tree.json(structPrepareTreeJS(inview_repo.struct))

    // for apps that live in the main dir
    render(`${PHP_SERVER}/${inview_repo.repo.id}`)

    
    checkInViewRepoWasEdited()
    .then(status => REPO_WAS_EDITED = status)
}

function displayRepoTree(struct) {
    let treeContainer = document.getElementById('tree')
    treeContainer.innerText = ""
    var tree = new Tree();
    tree.json(structPrepareTreeJS(struct))
}

function render(URL, refresh=false) {
    if(!refresh){
        killCodeServerView()
        BTN_TAB_RENDERER.click()
        BTN_TAB_CODE.classList.remove("disabled")
        if (inview_repo) runPreRenderUtilities(inview_repo.repo.id)
        if(renderer.src !== URL) // we only update if the URL changes. preventing unecessary reloads
            renderer.src = URL
    }
    else {
        renderer.src = URL
    }
}

function showSourceCode(port) {
    BTN_TAB_CODE.innerText = "Browsing code for " + inview_repo.repo.folder
    const URL = `${DEFAULT_SERVER}:${port}?folder=/${inview_repo.repo.folder}`
    // if (URL != source_code_viewer.src)
    if(source_code_viewer.src.indexOf(`:${port}`) == -1)
        poolStatus(async () => { 
            return await $.ajax({ 
                url: URL, 
                error: (e) => { console.log(e); return false}, 
                success: () => true }) 
            }, () => { 
                source_code_viewer.src = URL 
            }, 5)
}

function killCodeServerView() {
    source_code_viewer.src = ""
    BTN_TAB_CODE.innerText = "Code"
    BTN_TAB_CODE.classList.add("disabled")
    BTN_TAB_RENDERER.click()
}

function createOrUpdateRepoStudentInfo(data){
    return fetch(`/repo/${inview_repo.repo.id}/student`, {
        method: "POST",
        body: { ...data, csrfTokenMiddleware: CSRF_TOKEN }
    })
    .then(res => {
        if(!res.ok){
            notify("Failed to create or update repo's student info: " + res.responseText)
            return null
        }
        return res.json()
    })
}

function repoCheckoutBranch(repo_id, branch){
    // using query string because branch names can be tricky to handle
    return fetch(`/repo/${repo_id}/branches/checkout?b=${branch}`)
}

render("/stats")
