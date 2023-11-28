var socket = new WebSocket('ws://127.0.0.1:8000/ws/graph/');
socket.onmessage = function (e) {
    var djangoData = JSON.parse(e.data);
    console.log(djangoData);
    document.querySelector('#app').innerText = djangoData.value;
}