/** UI handling */
const resultListElement = document.querySelector("#search-result")
const renderer = document.querySelector("#renderer")
const home_frame = document.querySelector("#home-tab")
const BTN_TAB_RENDERER = document.querySelector("#btn-renderer-tab")
const BTN_TAB_CODE = document.querySelector("#btn-code-tab")
const source_code_viewer = document.querySelector("#source-code")
const NODE_ID_DISPLAY = document.querySelector("#repo-node-display")
const APACHE_URL_LINK = document.querySelector("#apache-url")
let APACHE_URL = undefined
const FRM_EDIT_ST_DETAILS = document.querySelector("[name=frm-edit-repo-st-info]")

let inview_repo = undefined
const DEFAULT_SERVER = location.origin
const PHP_SERVER = `${DEFAULT_SERVER}:3001`
let REPO_WAS_EDITED = 0
const CSRF_TOKEN = undefined
let listed_k_bases = []

function showSearchResults(results) {
    let html = ""
    if (results.length == 0) { html = "<p>No repository found.</p>" }
    else {
        results.forEach(repo => {
            html += `<li class="list-group-item repo-list-item" data-id="${repo.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${repo.full_name}">${repo.full_name.length < 20 ? repo.full_name : repo.full_name.substr(0, 20) + "..."}</li>`
        });
    }
    document.querySelector("#search-result").innerHTML = html
}

function displayRepo(repo_data) {
    // top, display repo name, user, and last updated time
    inview_repo = repo_data

    NODE_ID_DISPLAY.innerText = inview_repo.repo.id
    document.querySelector("#repo-about").innerHTML = repoAboutComponent(inview_repo.repo) + repoBranchManagamentComponent(inview_repo.repo)
    document.getElementById('tree').innerHTML = ""
    var tree = new Tree(document.getElementById('tree'));
    tree.json(structPrepareTreeJS(inview_repo.struct))

    // for apps that live in the main dir
    APACHE_URL=`${PHP_SERVER}/${inview_repo.repo.id}`
    render(APACHE_URL)

    APACHE_URL_LINK.href=APACHE_URL

    checkInViewRepoWasEdited()
        .then(status => REPO_WAS_EDITED = status)
}

function displayRepoTree(struct) {
    let treeContainer = document.getElementById('tree')
    treeContainer.innerText = ""
    var tree = new Tree();
    tree.json(structPrepareTreeJS(struct))
}

function render(URL, refresh = false, tab=undefined) {
    /**
     * Renders URL in specfied tab. By default uses renderer
     */
    if(!tab){ tab = "renderer"}
    const IFRAME = document.querySelector(`#${tab}`)
    if (!refresh) {
        if(tab=="renderer"){

            killCodeServerView()
            BTN_TAB_RENDERER.click()
            BTN_TAB_CODE.classList.remove("disabled")

            if (inview_repo) {
                runPreRenderUtilities(inview_repo.repo.id)
                APACHE_URL_LINK.style.display="block"
                APACHE_URL_LINK.style.cursor="pointer"
                APACHE_URL_LINK.href=URL
            }else {
                APACHE_URL_LINK.style.display="none"
                APACHE_URL_LINK.href=""
            }
            
            if (IFRAME.src !== URL) {// we only update if the URL changes. preventing unecessary reloads
                IFRAME.src = URL
            }
        }  
        else {
            IFRAME.src = URL
        }
    }
    else {
        IFRAME.src = URL
    }
}

function showSourceCode(port) {
    BTN_TAB_CODE.innerText = "Browsing code for " + inview_repo.repo.folder
    const URL = `${DEFAULT_SERVER}:${port}?folder=/${inview_repo.repo.folder}`
    // if (URL != source_code_viewer.src)
    if (source_code_viewer.src.indexOf(`:${port}`) == -1)
        poolStatus(async () => {
            return await $.ajax({
                url: URL,
                success: () => true,
                error: (e) => { console.log(e); return false }
            })
        }, () => {
            source_code_viewer.src = URL
        }, 5)
}

function killCodeServerView() {
    // only kill if the repo in view has changed
    if(source_code_viewer.src.indexOf(inview_repo.repo.folder) == -1) {
        source_code_viewer.src = ""
        BTN_TAB_CODE.innerText = "Code"
        BTN_TAB_CODE.classList.add("disabled")
        BTN_TAB_RENDERER.click()
    }
    else{
        console.log(`Cannot kill codeserver whilst repo in view has not changed`)
    }
}

function createOrUpdateRepoStudentInfo(data) {
    return fetch(`/repo/${inview_repo.repo.id}/student`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "X-CSRFToken": data.csrfmiddlewaretoken,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    })
        .then(res => {
            if (!res.ok) {
                notify("Failed to create or update repo's student info: " + res.statusText)
                return null
            }
            return res.json()
        })
}

function repoListItemClickHandler(event) {

    resultListElement.innerHTML = ""
    document.getElementById('tree').innerHTML = spinnerComponent()
    getRepository(event.target.dataset.id).then(data => { displayRepo(data) })
}


function repoCheckoutBranch(repo_id, branch) {
    // using query string because branch names can be tricky to handle
    return fetch(`/repo/${repo_id}/branches/checkout?b=${branch}`)
}

function loadKBases(search=null){
    getKBases(search)
    .then(bases => {
        listed_k_bases = bases
        let html = ""
        bases.forEach(base => {
            base_id = base.pk
            base = base.fields
            html += `
            <div class="accordion-item">
                <h2 class="accordion-header">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-base="${base_id}" data-bs-target="#base-${base_id}" aria-expanded="true" aria-controls="collapseOne">
                    ${ base.title }
                    <p class="k-base-title-foot">
                    by ${base.created_by}, last edited by ${base.last_edited_by} on the ${new Date(base.last_edited).toGMTString()}
                    </p>
                </button>
                </h2>
                <div id="base-${base_id}" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                    ${ base.text.replaceAll("\r\n", "<br/>").replaceAll("\n", "<br/>") }
                    <div class="row">
                        <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal"
                        data-bs-target="#k-base-form" data-base="${base_id}" id="k-base-edit">Edit</button>
                    </div>
                </div>
                </div>
            </div>`
        })

        document.querySelector("#k-base-main").innerHTML = `
        <div class="accordion" id="accordionExample">
            ${ search ? "seach result for <strong>" + search + '</strong> <button type="button" class="btn btn-outline-dark btn-sm mb-1 btn-clear-k-search">clear search</button>' : "Most populars knowledges" }
            ${html}
        </div>
        `
    })
}

updateAuthToken()
render("/stats", false, "home-tab")
loadKBases()
