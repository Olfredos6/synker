/** No UI handling */

function notify(message) {
    alert(message)
}

function searchRepo(keyword) {
    if(keyword.length > 0)
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
    return traverseUp(treeHTMLElement /*, treeHTMLElement.innerText */)
}

function repoAboutComponent(repo) {
    const updated_at = new Date(repo.last_updated)
    const link = `https://github.com/${repo.full_name}`
    return `
    <div class="card">
        <div class="card-footer text-muted repo-time">
        Last updated: <br/> ${updated_at.toDateString()} - ${updated_at.toLocaleTimeString()}
        </div>
        <div class="card-body">
            <h5 class="card-title">
                ${repo.name}
                <a href="${link}">${link}</a>
            </h5>
            <h6 class="card-subtitle mb-2 text-muted">${repo.owner}</h6>
            <p class="text-muted display-6" style="font-size: .9rem">${numberToReadable(repo.size)} Kb</p>
        </div>
    </div>
    `
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


function poolStatus(condition, callback, timeout=1) {
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
            }, timeout*1000)
        }
    }, 500)
}