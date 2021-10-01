setInterval(() => {
    /**
     * monitors the status of REPO_WAS_EDITED
     * and updates UI accodringly
     */
    const EDIT_STATUS_ELEMENT = document.querySelector("#edit-status")
    if(inview_repo){EDIT_STATUS_ELEMENT.style.display = "block"}
    else{EDIT_STATUS_ELEMENT.style.display = "none"}
    switch(REPO_WAS_EDITED){
        case -1: EDIT_STATUS_ELEMENT.innerText = "Could not check repo edit status";
        break;
        case 0: EDIT_STATUS_ELEMENT.innerText = "No local changes";
        break;
        case 1: EDIT_STATUS_ELEMENT.innerText = "Repo has non-remote changes";
        break;
        default:{
            EDIT_STATUS_ELEMENT.innerText = "";
        }
    }
}, 3000);