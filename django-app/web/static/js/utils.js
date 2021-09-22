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

function spinner(text = "Spinning...") {
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