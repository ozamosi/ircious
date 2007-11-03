function setFavourite(object) {
    id = object.id.substr(10);
    var request = new XMLHttpRequest();
    request.open('GET', '/'+id+'/favourite/', true);
    request.onreadystatechange = function()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            if (object.className.baseVal == "selected")
            {
                object.className.baseVal = "not-selected";
            }
            else
            {
                object.className.baseVal = "selected";
            }
        }
    }
}
