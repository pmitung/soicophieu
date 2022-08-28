var loc = window.location

var wsStart = 'ws://'
if (loc.protocol == 'https:'){
    wsStart = 'wss://'
}

var endpoint = wsStart + loc.host + loc.pathname;
// var endpoint = 'wss://127.0.0.1:6379'
var socket = new WebSocket(endpoint);

socket.onmessage = function(e){
    console.log("connect", e);

    var viewData = JSON.parse(e.data);

    newviewChart.config.data.datasets[0].data = viewData.value;
    newviewChart.update();

    
    document.querySelector('#total-viewcount').innerText = String(viewData.total_viewcount).concat(" ", "lượt xem");
    document.querySelector('#comm-pos-t1').innerText = String(viewData.comm_pos_percent_T1).concat("%");
    console.log(viewData.comm_pos_percent_T1)
    document.querySelector('#comm-pos-t3').innerText = String(viewData.comm_pos_percent_T3).concat("%");
    document.querySelector('#comm-neg-t1').innerText = String(viewData.comm_neg_percent_T1).concat("%");
    document.querySelector('#comm-neg-t3').innerText = String(viewData.comm_neg_percent_T3).concat("%");
}

socket.onopen = function(e){
    console.log("open", e)
}

socket.onerror = function(e){
    console.log("error", e)
}

socket.onclose = function(e){
    console.log("close", e)
}
