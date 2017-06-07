/**
 * Created by ephtron on 30.05.17.
 */

// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.


// class LoggedPlayerLogic{
//     constructor(players, width) {
//     this.players = players;
//   }
// }

function process_old_events(val) {
    // test = "{ 'players' :"+val +"}";
    console.log("received: ", val);
    // console.log("test to json",test);

    //check = eval("(" + val + ")");
    //console.log("c1:", check);
    check2 = JSON.parse(val);
    console.log("c2:", check2);
}

$(document).ready(function () {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function () {
    };

    $("#eventform").on("submit", function () {
        newEvent($(this));
        return false;
    });
    $("#eventform").on("keypress", function (e) {
        if (e.keyCode == 13) {
            newEvent($(this));
            return false;
        }
        return true;
    });


    $("#event").select();
    updater.poll();
});

function newEvent(form) {
    var message = form.formToDict();
    var disabled = form.find("input[type=submit]");
    disabled.disable();
    $.postJSON("/event/new", message, function (response) {
        //updater.showEvent(response);
        if (message.id) {
            form.parent().remove();
        } else {
            form.find("input[type=text]").val("").select();
            disabled.enable();
        }
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function (url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({
        url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function (response) {
            if (callback) callback(eval("(" + response + ")"));
        }, error: function (response) {
            console.log("ERROR:", response);
        }
    });
};

jQuery.fn.formToDict = function () {
    var fields = this.serializeArray();
    var json = {};
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

jQuery.fn.disable = function () {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function (opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};

var updater = {
    errorSleepTime: 500,
    cursor: null,
    poll: function () {
        var args = {"_xsrf": getCookie("_xsrf")};
        if (updater.cursor) args.cursor = updater.cursor;
        $.ajax({
            url: "/event/update", type: "POST", dataType: "text",
            data: $.param(args),
            success: updater.onSuccess,
            error: function (xhr, status, error, exception) {
                console.log("response" + xhr.responseText);
                // var err = eval("(" + xhr.responseText + ")");
                // alert('Exeption:'+exception);
                console.log('Status:' + status);
                console.log('error:' + error);
                console.log('exception:' + exception);
            }

            //updater.onError
        });
    },

    onSuccess: function (response) {
        response_json = JSON.parse(response);
        console.log("Success", response_json);
        try {
            updater.newEvents(response_json);
        } catch (e) {
            console.log("yes", e);
            updater.onError();
            return;
        }
        updater.errorSleepTime = 500;
        window.setTimeout(updater.poll, 0);
    },

    onError: function (response) {
        updater.errorSleepTime *= 2;
        // console.log("Error with response:", response);
        // console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newEvents: function (response) {

        console.log("events:", response.events);
        console.log("New Events:", response);
        //if (!response.events) return;

        updater.cursor = response.cursor;

        var events = response.events;
        updater.cursor = events[events.length - 1].id;
        console.log(events.length, "new messages, cursor:", updater.cursor);
        for (var i = 0; i < events.length; i++) {
            updater.showEvent(events[i]);
        }
    },

    showEvent: function (event_json) {
        console.log("Show Events:", event_json);

        // Todo: process events according to the given informations -> check Event.py, also adjust <div> to <p>...
        var text = document.createElement("div");
        text.innerHTML = event_json.sender_name + ": " + event_json.body;
        if (event_json.type === 'player-entered') {
            $("#players").append(text);
        } else if (event_json.type === 'message') {
            $("#event-log").append(text);
        }
    }
};
