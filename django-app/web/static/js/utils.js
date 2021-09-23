/** No UI handling */

function notify(message) {
    alert(message)
}

function searchRepo(keyword) {
    return fetch(`/search?keyword=${keyword}`)
        .then(res => {
            if (!res.ok) {
                notify(res.status + " - " + res.statusText)
                return []
            }
            return res.json()
        })
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

function spinnerComponent(text = "Spinning...") {
    return `
    <div class="mx-auto mt-2">
        <div class="spinner-border" role="status">
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
    return `
    <div class="card">
        <div class="card-footer text-muted repo-time">
        Last updated: <br/> ${updated_at.toDateString()} - ${updated_at.toLocaleTimeString()}
        </div>
        <div class="card-body">
            <h5 class="card-title">${repo.name}</h5>
            <h6 class="card-subtitle mb-2 text-muted">${repo.owner}</h6>
            <p class="text-muted display-6" style="font-size: .9rem">${numberToReadable(repo.size)} Kb</p>
        </div>
    </div>
    `
}

function numberToReadable(number){
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