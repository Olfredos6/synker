/** No UI handling */

GET_TOKEN = () => localStorage.getItem("AUTH_TOKEN")

function notify(message) {
    alert(message)
}

function searchRepo(keyword) {
    if (keyword.length > 0)
        return fetch(`/search?keyword=${keyword}`)
            .then(res => {
                if (!res.ok) {
                    notify(res.status + " - " + res.statusText)
                    return []
                }
                return res.json()
            })
    else
        return []
}

function getRepository(id) {
    /**
     * collects necessary data about a repository. That is:
     * - repo object data
     * - repo directory structure
     */
    return fetch(`/repo/${id}`)
        .then(res => {
            if (!res.ok) {
                notify(res.status + " - " + res.statusText)
                return { repo: undefined, struct: undefined }
            }
            return res.json()
        })
}

function spinnerComponent(text = "Spinning...", size = 2) {
    return `
    <div class="mx-auto mt-2">
        <div class="spinner-border" style="height: ${size}rem; width: ${size}rem" role="status">
            <span class="sr-only"></span>
        </div>
        <span>${text}</span>
    </div>`
}

function structPrepareTreeJS(struct) {
    /**
     * Prepares a struct as received from server
     * to work with Tree.js
     */
    //  treeStruct = []
    //  for (entry in struct)
    //      repr = []
    function traverse(data) {
        let tree = []
        for (topentry in data) {
            if (topentry == "-") {
                for (entry of data["-"]) {
                    tree.push({
                        name: entry
                    })
                }
            } else {
                tree.push({
                    name: topentry,
                    type: Tree.FOLDER,
                    children: traverse(data[topentry])
                })
            }
        }
        return tree
    }
    return traverse(struct)
}

function rebuildDirPath(treeHTMLElement) {
    /**
     * Rebuilds a string matching the clicked element in
     * displayed directory tree
     */

    function traverseUp(element, path = "") {
        // if(element.firstElementChild.innerText !== ""){
        //     path = element.innerText  + "/" +  path
        const summaryElement = element.parentElement.children[0]
        if (summaryElement.nodeName === 'SUMMARY' && summaryElement.innerText !== "") {
            path = traverseUp(summaryElement.parentElement, summaryElement.innerText + "/" + path)
        }
        // }
        return path
    }
    return traverseUp(treeHTMLElement , treeHTMLElement.nodeName === 'SUMMARY' ? "" : treeHTMLElement.innerText )
}

function repoAboutComponent(repo) {
    const updated_at = new Date(repo.last_updated)
    const link = `https://github.com/${repo.full_name}`

    let student_details = "<p class='text-muted'>Student details not recorded yet!</p>"
    if (!repo.student.detail) {
        student_details = `
        <div class="student-details">
            <p>${repo.student.name + " " + repo.student.surname}</p>
            <p>${repo.student.customer_no}</p>
            <p>${repo.student.email}</p>
        </div>
        `
    }
    return `
    <div class="card">
        <div class="card-footer text-muted repo-time">
            <div class="repo-controls">
                <i class="bi bi-arrow-repeat" id="repo-reload" data-bs-toggle="tooltip" data-bs-placement="top" title="Reload repository"></i>
                <i class="bi bi-pencil-square edit-repo-info" data-bs-toggle="modal" data-bs-target="#modal-repo-info"></i>
                <i class="bi bi-exclamation-circle reviews-n-issues" title="Reviews and Issues"></i>
            </div>
            Last updated: <br/> ${updated_at.toDateString()} - ${updated_at.toLocaleTimeString()}
        </div>
        <div class="card-body">
            <h5 class="card-title">
                ${repo.name}
                <a href="${link}" target="_blank">${link}</a>
            </h5>
            <h6 class="card-subtitle mb-2 text-muted">${repo.owner}</h6>
            <p class="text-muted display-6" style="font-size: .9rem">${numberToReadable(repo.size)} Kb</p>
            <hr>
            ${student_details}
        </div>
    </div>
    `
}


async function reviewsAndIssuesComponent() {
    let html = ''
    let opened_issues_html = ''
    tasks = await getReviewTaskListJSON()
    opened_issues = await fetch(`/review-issues/${GET_TOKEN()}?repo=${inview_repo.repo.id}`).then( res => res.json())
    opened_issues.forEach( issue => {
        opened_issues_html += `
        <li class="list-group-item">
            ${ issue.title }
            <div>
                <p class="card-text text-muted my-0">Opened on the ${(new Date(issue.created_at)).toLocaleString()}</p>
                <p class="card-text text-muted my-0">Closed on the ${(new Date(issue.closed_at)).toLocaleString()}</p>
            </div>
        </li>`
    })

    tasks.forEach(t => {
        html += "<option value='" + t.name + "'>" + t.name + "</option>"
    })

    return `<div class="card card-reviews-issues" style="position: absolute;top: 5vh;height: 75vh; z-index: 1000; width: 16%">
                <div class="card-footer">
                    <button type="button" class="btn btn-danger btn-sm float-end" id="btn-close-rev-n-issues">Quit</button>
                </div>
                <div class="card-body">
                    <div class="mb-4">
                        <h6 class="card-subtitle mb-2 text-muted">Open issues</h6>
                        <div id="open-issues">
                            ${opened_issues_html}
                        </div>
                    </div>
                    <h6 class="card-subtitle mb-2 text-muted">New issue/review as:</h6>
                    <select class="form-select" aria-label="Default select example" id="review-sel-project">
                        <option>Choose a project to review</option>
                        ${html}
                    </select>
                    <div id="review-tasks">

                    </div>
                </div>
            </div>`
}


function repoBranchManagamentComponent(repo) {
    /**
     * Displays branching info and management
     * options such as branch checkout
     */
    return `
    <div class="card">
        <div class="card-footer text-muted repo-time">
            Current Branch: <br/> ${repo.current_branch}
        </div>
        <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Switch branches:</h6>
            <select class="form-select" aria-label="Default select example" id="sel-switch-branch">
                <option selected>${repo.current_branch}</option>
                ${repo.branches.splice(1).map(branch => `<option value="${branch}">${branch}</option>`)}
            </select>
        </div>
    </div>
    `

}

function formToJSON(form_name) {
    let formData = new FormData(document.querySelector(`[name=${form_name}]`))
    let jsonData = {}
    formData.forEach((value, key) => {
        if (!isNaN(value)) {
            if (value.indexOf(".")) value = parseFloat(value)
            else { value = parseInt(value) }
        }
        jsonData[key] = value
    })
    return jsonData
}

function numberToReadable(number) {
    let formated_number = NaN
    if (number !== "") {
        try {
            if (typeof (number) != "number") number = parseFloat(number)
            formated_number = (Math.round((number + Number.EPSILON) * 1000) / 1000).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
        }
        catch (e) {
            console.log("Failed to format number.");
        }
    }
    else {
        formated_number = ""
    }
    return formated_number
}

function overrideGeolocationAPIgetCurrentPosition(coordinates) {
    /**
     * @param coordinates: {latitude: float, longitude: float}
     * This funcions overrides the native Geolocation API 
     * getCurrentPosition
     */
    navigator.geolocation.getCurrentPosition = function () {
        return coordinates
    }

    return 0
}

function runPreRenderUtilities(id) {
    return fetch(`/pre-render/${id}`)
        .then(res => {
            if (res.ok) return true
            else { return false }
        })
}

function requestCodeServer(node_id) {
    /**
     * Sends a request to start a code-server instance or get the one on the repo with the given node_id.
     * If the request was successfull, the reponse holds the port on which the server is running
     */
    return fetch(`/code-server/${node_id}`)
        .then(res => {
            if (res.ok) return res.json()
            else { return false }
        })
}

function killCodeServer(node_id) {
    /**
     * Sends a request to kill a code-server instance on the repo with the given node_id.
     */
    return fetch(`/kill-code-server/${node_id}`)
        .then(res => {
            if (res.ok) return res.json()
            else { false }
        })
}


function poolStatus(condition, callback, timeout = 1) {
    /**
     * @param timeout in seconds
     */
    document.querySelector("body").insertAdjacentHTML(
        "afterEnd",
        `<div id="loader" style="
            position: absolute;
            top: 50%;
            left: 50%;"
        >${spinnerComponent("starting code-server...", 6)}
        </div>`
    )
    condition = condition
    interval = setInterval(function () {
        if (condition()) {
            clearInterval(interval)
            setTimeout(() => {
                document.querySelector("#loader").remove()
                callback()
            }, timeout * 1000)
        }
    }, 500)
}

function checkInViewRepoWasEdited() {
    /**
     * sends a request to check if the repo in view was edited.
     * returns:
     *  0 if not
     *  1 if true
     *  -1 if the request failed
     */


    return fetch(`/repo/${inview_repo.repo.id}/was_edited`)
        .then(res => {
            if (!res.ok) {
                console.log("Could not check this repo was edited", res.status, res.statusText)
                return { "was_edited": -1 }
            }
            return res.json()
        })
        .then(data => { REPO_WAS_EDITED = data.was_edited; return data.was_edited })

}

function updateAuthToken() {
    let arr = location.pathname.split("/")
    let token = arr[arr.length - 1]
    localStorage.setItem("AUTH_TOKEN", token)
}

function getKBases(search = null) {
    return fetch(`/knowledge-base/${GET_TOKEN()}${search ? '?search=' + search : ''}`)
        .then(res => res.json())
        .then(data => data)
}

function incrementBaseViewCount(base_id) {
    fetch(`/knowledge-base/up-count/${GET_TOKEN()}?id=${base_id}`)
}


function fillKBaseFormWith(base) {
    id = base.pk
    base = base.fields
    document.querySelector("[name='k-base-frm']").id.value = id
    document.querySelector("[name='k-base-frm']").title.value = base.title
    document.querySelector("[name='k-base-frm']").text.value = base.text
    document.querySelector("[name='k-base-frm']").tags.value = base.tags
}

function getReviewTaskListJSON() {
    return fetch("/static/js/issue-task-list.json")
        .then(res => res.json())
        .then(d => d)
}


function getPorjectReviewList(project_name){
    return fetch("/static/js/issue-task-list.json")
    .then(res => res.json())
    .then(d => d.find( project => project.name == project_name ).tasks)
}

function displayProjectReviwList(list){
    let html = `<p class="my-2">
                    <strong>Select tasks to complete on this project</strong>
                </p>
                <form name="frm-issue-task-list">`
    list.forEach( (task, index) => {
        html += `
        <div class="form-check">
            <input class="form-check-input" type="checkbox" name="t-${ index }" value="${ index }" id="task-${ index }">
            <label class="form-check-label" for="task-${ index }">
                ${ task }
            </label>
        </div>`
    })
    document.querySelector(".card-reviews-issues .card-body #review-tasks").innerHTML = html + `</form>
    <div class="d-grid gap-2">
        <button class="btn btn-primary btn-small" type="button" id="btn-submit-new-issue">Submit new issue</button>
        <button class="btn btn-warning btn-small" type="button" data-bs-toggle="modal" data-bs-target="#review-email-text" id="btn-get-issue-text">Get text for email</button>
    </div>
    `
}


function getMostPopularRepos(){
    return fetch(`/repo/most-populars/${GET_TOKEN()}`)
    .then( res => {
        if(res.ok) return res.json()
        else return []
    })
}
