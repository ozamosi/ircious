function setFavourite(object)
{
    var id = object.parentNode.getAttribute("id").substr(3, object.parentNode.getAttribute("id").length-4);
    var request = new XMLHttpRequest();
    request.open('POST', '/'+id+'/favourite/', true);
    request.onreadystatechange = function()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            var thisg = object.parentNode;
            var fullid = thisg.getAttribute("id");
            if (fullid.substr(fullid.length-1) == "n")
            {
                thisg.setAttribute("display", "none");
                otherg = document.getElementById(fullid.substr(0, fullid.length-1)+"s")
                otherg.setAttribute("display", "inline");
            }
            else
            {
                thisg.setAttribute("display", "none");
                otherg = document.getElementById(fullid.substr(0, fullid.length-1)+"n")
                otherg.setAttribute("display", "inline");
            }
        }
    }
    request.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
    request.send("Id: "+id);
}
