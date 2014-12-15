/**
 * Copyright (c) 2014 - Charles `sparticvs` Timko
 */
var CONFIG_FILE = "../etc/server.js";

var CONFIG = {
    "http" : {
        "addr" : "0.0.0.0",
        "port" : 1234
    },
    "webs" : {
        "addr" : "0.0.0.0",
        "port" : 2345
    }
}


var http = require('http');
var websock = require('ws');
var fs = require('fs');

var data = {
    "jobs": [
        {
            "name": "foobar",
            "build": {
                "status": "success",
                "timestamp": "2014-03-10T19:45:46+0000",
                "label": "#4123",
                "cause": "Build was started by SCM change"
            },
            "repo": {
                "branch": "master",
                "commit": "abcdef0123456789",
                "blame": "sparticvs",
                "timestamp": "2014-03-10T19:44:46+0000",
            }
        },
        {
            "name": "barbaz",
            "build": {
                "status": "failure",
                "timestamp": "2014-03-10T19:45:46+0000",
                "label": "#1241",
                "cause": "Build was started by timer"
            },
            "repo": {
                "branch": "experimental",
                "commit": "abcdef0123456789",
                "blame": "sparticvs",
                "timestamp": "2014-03-10T19:44:46+0000",
            }
        }
    ]
};

var server = http.createServer(function(req, res) {
    res.write(JSON.stringify(data, null, 4));
    res.end();
});

server.listen(1234);
