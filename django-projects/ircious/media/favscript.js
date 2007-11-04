function setFavourite(object)
{
    var id = object.id.substr(10);
    var request = new XMLHttpRequest();
    request.open('POST', '/'+id+'/favourite/', true);
    request.onreadystatechange = function()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            toggleClass(object);
        }
    }
    request.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
    request.send("Id: "+id);
}

function toggleClass(object)
{
    if (object.className.baseVal == "selected")
    {
        object.className.baseVal = "not-selected";
    }
    else
    {
        object.className.baseVal = "selected";
    }
    // What the hell is wrong with opera!?
}
