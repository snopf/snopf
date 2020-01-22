// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

// The background script has three responsibilities:
// a) tunneling requests from the menu to the native app and back
// b) storing the account table and giving it to the menu script
// c) storing the pin (if set)

function dbg_message(msg)
{
    console.log('SNOPF_BACKGROUND: ' + msg);
}

// We will save the pin here (if chosen by the user)
var saved_pin = '';

// The current account table, we'll get it from the native app on startup
var account_table = {}

// Connection for native app
var port_driver = chrome.runtime.connectNative('com.snopf.snopf');

// Connection to menu script
var snopf_background_port;

port_driver.onMessage.addListener((message) => {
    dbg_message('Native -> Background: ' + JSON.stringify(message));
    
    switch (message.cmd) {
        // TODO alerts from background script work for chrome but not firefox
        case 'error':
            window.alert(message.msg);
            window.close();
            break;
        // We manage the account table
        case 'get_account_table':
            account_table = message.msg;
            break;
            
        // just pass it through to the menu script
        default:
            snopf_background_port.postMessage(message);
    }
});

// Delete the saved pin
function reset_pin()
{
    dbg_message('Erasing saved pin');
    saved_pin = '';
}

// Save the pin (if this option is selected)
function save_pin(pin)
{
    saved_pin = pin;
    chrome.storage.sync.get('save_pin_active_session', function(items) {
        if (!(items.save_pin_active_session)) {
            reset_pin();
        }
    });
}

// Handle messages from the menu
function connected(p) {
    snopf_background_port = p;
    snopf_background_port.postMessage({cmd: 'debug', msg: 'Hello'});
    
    snopf_background_port.onMessage.addListener((message) => {
        dbg_message('Menu -> Background: ' + JSON.stringify(message));
        
        switch (message.cmd) {
            // We will provide the pin if we can
            case 'request_pin':
                snopf_background_port.postMessage(
                    {cmd: message.cmd, msg: saved_pin});
                break;
            
            // Transfer account table to menu
            case 'get_account_table':
                snopf_background_port.postMessage(
                    {cmd: message.cmd, msg: account_table});
                break;
                
            // We will change the stored pin on request
            case 'change_pin':
                save_pin(message.msg);
                break;
                
            // Every other message we'll tunnel directly to the native app
            default:
                port_driver.postMessage(message);
        }
    });
}

chrome.runtime.onConnect.addListener(connected);

// First get the account table from the native app
port_driver.postMessage({cmd: 'get_account_table', msg:''});

dbg_message('started');
