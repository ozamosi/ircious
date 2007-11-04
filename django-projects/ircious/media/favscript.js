function setFavourite(object)
{
    var id = object.parentNode.getAttribute("id").substr(3, object.parentNode.getAttribute("id").length-1);
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

function toggle(object)
{
    var thisg = object.parentNode;
    var id = thisg.getAttribute("id");
    if (id.substr(id.length-1) == "n")
    {
        thisg.setAttribute("display", "none");
        otherg = document.getElementById(id.substr(0, id.length-1)+"s")
        otherg.setAttribute("display", "inline");
    }
    else
    {
        thisg.setAttribute("display", "none");
        otherg = document.getElementById(id.substr(0, id.length-1)+"n")
        otherg.setAttribute("display", "inline");
    }

}
