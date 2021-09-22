/** No UI handling */

function searchRepo(keyword){
    return fetch(`/search?keyword=${keyword}`)
    .then( res => {
        if(!res.ok){
            alert(res.status, res.statusText)
            return []
        }
        return res.json()
    })
}

function spinner(text="Spinning..."){
    return `
    <div class="mx-auto mt-2">
        <div class="spinner-border" role="status">
            <span class="sr-only"></span>
        </div>
        <span>${text}</span>
    </div>`
}