// Parse an HTML5-liberalized version of RFC 3339 datetime values
Date.parseRFC3339 = function (string) {
    var date=new Date(0);
    var match = string.match(/(\d{4})-(\d\d)-(\d\d)\s*(?:[\sT]\s*(\d\d):(\d\d)(?::(\d\d))?(\.\d*)?\s*(Z|([-+])(\d\d):(\d\d))?)?/);
    if (!match) return;
    if (match[2]) match[2]--;
    if (match[7]) match[7] = (match[7]+'000').substring(1,4);
    var field = [null,'FullYear','Month','Date','Hours','Minutes','Seconds','Milliseconds'];
    for (var i=1; i<=7; i++) if (match[i]) date['setUTC'+field[i]](match[i]);
    if (match[9]) date.setTime(date.getTime()+
        (match[9]=='-'?1:-1)*(match[10]*3600000+match[11]*60000) );
    return date.getTime();
}

// Localize the display of <time> elements
function localizeDates() {
  var xhtml = "http://www.w3.org/1999/xhtml";
  var times = document.getElementsByTagNameNS(xhtml,'time');
  var lastdate = '';
  var now = new Date();

  for (var i=0; i<times.length; i++) {
    if (times[i].getAttribute('title') == "GMT") {
      var date = new Date(Date.parseRFC3339(times[i].getAttribute('datetime')));
      if (!date.getTime()) return;

      // replace title attribute and innerHTML value with localized versions
      if (times[i].innerHTML.length < 10 || now-date < 86400000) {
        // time only
        times[i].setAttribute('title', date.toUTCString());
        times[i].innerHTML = date.toLocaleTimeString();
      } else if (times[i].getAttribute('datetime').length <= 16) {
        // date only
        times[i].removeAttribute('title');
        times[i].innerHTML = date.toLocaleDateString();
      } else {
        // full datetime
        times[i].setAttribute('title', times[i].innerHTML + ' GMT');
        times[i].innerHTML = date.toLocaleString();
      }

      // insert/remove date headers to reflect date in local time zone
      var parent = times[i];
      while (parent && parent.nodeName != 'div') parent=parent.parentNode;
      if (parent && parent.getAttribute('class')=='comment') {
        sibling = parent.previousSibling;
        while (sibling && sibling.nodeType != 1) {
           sibling = sibling.previousSibling;
        }

        var header = date.toLocaleDateString();
        var datetime = times[i].getAttribute('datetime').substring(0,10);
        if (sibling && sibling.nodeName.toLowerCase() == 'h2') {
          if (lastdate == header) {
            sibling.parentNode.removeChild(sibling);
          } else {
            sibling.childNodes[0].innerHTML = header;
            sibling.childNodes[0].setAttribute('datetime',datetime);
          }
        } else if (lastdate != header) {
          var h2 = document.createElement('h2');
          var time = document.createElement('time');
          time.setAttribute('datetime',datetime);
          time.appendChild(document.createTextNode(header));
          h2.appendChild(time);
          parent.parentNode.insertBefore(h2, parent);
        }
        lastdate = header;
      }
    }
  }
}

if (document.addEventListener) {
  document.addEventListener("DOMContentLoaded", localizeDates, false);
}
