"use strict";

var CCR = {
    init: function(send_function) {
        this.send = send_function;
        this.queue = {};
        this.id_counter = 0;
    },
    process: function(data) {
        var message_id = parseInt(data['message_id']);
        for (var i in this.queue) {
            if (i == message_id) {
                this.queue[i].call(this, JSON.parse(data['body']), data['status_code']);
                delete this.queue[i];
            }
        }
    },
    request: function(method, url, callback, payload) {
        this.id_counter++;
        var data = {
            "datatype": "request",
            "message_id": this.id_counter,
            "url": url,
            "method": method
        }
        this.queue[this.id_counter] = callback;
        this.send(JSON.stringify(data));
    },
    get: function(url, callback) {
        return this.request("GET", url, callback, null);
    },
    post: function(url, payload, callback) {
        return this.request("POST", url, callback, payload);
    }
};
