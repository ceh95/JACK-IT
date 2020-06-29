function makeGetRequest(url, readyStateMethod) {
    var httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
        alert('Cannot create an XMLHTTP instance');
        return false;
    }
    
    httpRequest.onreadystatechange = function() {readyStateMethod(httpRequest)};
    httpRequest.open("GET", url);
    httpRequest.send();
}

function makePostRequest(url, readyStateMethod, data) {
    var httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
        alert('Cannot create an XMLHTTP instance');
        return false;
    }
    
    httpRequest.onreadystatechange = function() {readyStateMethod(httpRequest)};
    httpRequest.open("POST", url);
    httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    httpRequest.send(data);
}

function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}