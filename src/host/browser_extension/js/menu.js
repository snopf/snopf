// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

function dbg_message(msg)
{
    console.log('SNOPF-MENU: ' + msg);
}

// JSON of hostname : accounts
var accounts = null;

// This is true if we want to create new entries with the browser plugin
var add_new_entries = false;

// Port to use for websocket
var websocket_port = null;

// Our ID to identify to websocket server
var websocket_id = null;

// Automatically hit enter after typing in the password
var hit_enter = false;

// Websocket to Snopf QT
var webSocket = null;

// Guess for the service name to use
var service_guess = '';

// Guess for the account
var account_guess = '';

// Set the optional variables and open a websocket after retrieving options
function set_options(items) {
    add_new_entries = items.add_new_entries;
    if (add_new_entries) {
        $('#button-ok').prop('disabled', false);
    }
    websocket_port = items.websocket_port;
    hit_enter = items.hit_enter;
    webSocket = new WebSocket('ws://localhost:' + String(websocket_port));
    websocket_id = items.websocket_id;
    webSocket.onopen = websocket_onopen;
    webSocket.onerror = websocket_onerror;
    webSocket.onmessage = websocket_onmessage;
}

// Send message over websocket
function websocket_send_message(msg)
{
    msg['id'] = websocket_id;
    webSocket.send(JSON.stringify(msg));
}

// Get the current options
function get_options()
{
    chrome.storage.sync.get({
        'add_new_entries': true,
        'hit_enter': false,
        'websocket_port': 60100,
        'websocket_id': ''},
        set_options);
}

// Connection successful, get account table entries from server
function websocket_onopen(event)
{
    $('#no-snopf-server-notice').hide();
    $('#device-not-connected-notice').show();
    websocket_send_message({cmd: 'get-accounts'});
}

// Error handler for websocket connection
function websocket_onerror(event) {
    console.error('WebSocket error:', event);
}

// Process answers from websocket server
function websocket_onmessage (event) {
    msg = JSON.parse(event.data)
    switch (msg.cmd) {
        case 'new-accounts':
            accounts = msg.data;
            websocket_send_message({cmd: 'get-device-available'});
            $('#input-service').autocomplete({source: Object.keys(accounts)});
            $('#input-service').val(service_guess);
            fill_account_suggestions();
            if (account_guess) {
                $('#input-account').val(account_guess);
            }
            check_if_new();
            break;
        case 'device-available':
            if (msg.data['device-available'] == true) {
                $('#device-not-connected-notice').hide();
                $('#form').show();
            }
            break;
    }
}

// Port for communication with the content script to gather possible information
// about the login name and to signal the termination of the menu script
// to allow the content script to refocus on the password field
var content_port = null;
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var active_tab = tabs[0];
    content_port = chrome.tabs.connect(
        active_tab.id, {name: 'snopf-content-port'});
});

// Handler for messages from the content script
function content_port_message_handler(message) {
    dbg_message('Content -> Menu: ' + JSON.stringify(message));

    switch (message.cmd) {
        case 'error':
            window.alert(message.msg);
            window.close();
            break;

        case 'website-info':
            service_guess = (message.msg['hostname']);
            account_guess = message.msg['username'];
            break;
    }
}

// Get current hostname and possible username from content script
function request_website_info() {
    // We eventually initialize the content port here
    // But we don't want to wait for our content script if the user clicks
    // on the button faster than the webpage loading time we'll just
    // skip the content script part
    if (content_port) {
        content_port.onMessage.addListener(content_port_message_handler);
        content_port.postMessage({cmd: 'website-info'});
    }
}

// Send password request to snopf server
function send_request() {
    var req = gui_input_to_request();
    req.hit_enter = hit_enter;
    req.add_new_entries = add_new_entries;
    msg = {cmd: 'password-request', data: req};
    websocket_send_message(msg);

    // Refocus on the password field on the website
    if (content_port) {
        try {
            content_port.postMessage({cmd: 'refocus'});
        } catch (e) {
            dbg_message('Cannot connect to content script');
        }
    }

    window.close();
}

// Set autocomplete for possible accounts
function fill_account_suggestions()
{
    $('#input-account').val('');
    var service = $('#input-service').val();
    if (accounts[service]) {
        $('#input-account').autocomplete(
            {source: accounts[service], minLength: 0});
        $('#input-account').val(accounts[service][0]);
    } else {
        $('#input-account').attr('autocomplete', 'off');
    }
}

// Check if the current service / account combination is new and show a warning
// if necessary
function check_if_new()
{
    if (Object.keys(accounts).includes(get_service())) {
        if (accounts[get_service()].includes(get_account())) {
            $('#new-entry-warning').hide();
            $('#no-such-entry-warning').hide();
            $("#input-service").removeClass('w3-pale-red');
            $("#input-account").removeClass('w3-pale-red');
            $("#input-service").addClass('w3-light-grey');
            $("#input-account").addClass('w3-light-grey');
            // We enable the button if we only allow request of existing entries
            $('#button-ok').prop('disabled', false);
            return;
        }
    }
    $("#input-service").removeClass('w3-light-grey');
    $("#input-account").removeClass('w3-light-grey');
    $("#input-service").addClass('w3-pale-red');
    $("#input-account").addClass('w3-pale-red');
    // We enable the button if we only allow request of existing entries
    if (!add_new_entries) {
        $('#button-ok').prop('disabled', true);
        $('#no-such-entry-warning').show();
    } else {
        $('#new-entry-warning').show();
    }
}

$('#input-service').change(function() {
    check_if_new();
})

$('#input-account').change(function() {
    check_if_new();
})

$('#input-service').focusout(function() {
    fill_account_suggestions();
    check_if_new();
})

$('#input-account').focusout(function() {
    check_if_new();
})

// Get the currently selected service
function get_service() { return $('#input-service').val(); }

// Get the currently selected account
function get_account() { return $('#input-account').val();}


// Read the input fields and build a JSON message
function gui_input_to_request() {
    return {
        'service': get_service(),
        'account': get_account()
    }
}

// Entry point of menu script
$(document).ready(function() {
    // Bind the submit event to a password request
    $('#form').submit(send_request);
    request_website_info();
    // Start by getting the options
    get_options();
});
