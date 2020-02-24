// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

function dbg_message(msg)
{
    console.log('SNOPF_MENU: ' + msg);
}

// Port for communication with the background script (which in turn uses
// native messaging to communicate with the USB driver)
var background_port = chrome.runtime.connect({name: 'snopf_background_port'});

// Port for communication with the content script to gather possible information
// about the login name and to signal the termination of the menu script
// to allow the content script to refocus on the password field
var content_port = null;
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var active_tab = tabs[0];
    content_port = chrome.tabs.connect(
        active_tab.id, {name: 'snopf_content_port'});
});

// Account table, we'll get it from the background script
var account_table = {};

// Options for the extension
var options;

// Get the currently selected hostname
function get_hostname() { return $('#input_hostname').val(); }

// Get the currently selected account
function get_account() { return $('#input_account').val();}

// Check if we want to save new login data
function check_new_info_save() 
{
    return $('#checkbox_save_info').prop('checked');
}

// If the account input changed we might have to update the
// current password settings (length + iteration)
function update_password_settings()
{
    hostname = get_hostname();
    account = get_account();
    if ((hostname in self.account_table)
        && (account in self.account_table[hostname])) {
        $('#password_length').val(
            account_table[hostname][account]['password_length']);
        $('#password_iteration').val(
            account_table[hostname][account]['password_iteration']);    
    }
    else {
        // Reset to standard values if the account name is unknown
        $('#password_length').val(40);
        $('#password_iteration').val(0);
    }
}
    

// Changes in account / hostname field should update the read data
function init_gui_change_events() {
    // If the hostname changes, we have to rebuild the popup
    $('#input_hostname').change(function() {
        fill_out_accounts($(this).val());
    });
    
    // Update settings according to selected account
    $('#input_account').change(update_password_settings);

    // Activate the account selection change event
    $('#select_account').change(function() {
        // Set the input text to the selected account
        $('#input_account').val($(this).val());
        // Set the selection to the info text
        $('#select_account_option').prop('selected', true);
        // Trigger the input change to update the password settings if
        // necessary
        $('#input_account').trigger('change');
    });
}

// Clear the accounts combobox
function clear_accounts()
{
    // Clear the select except for the dummy 'Select account' entry
    old_options = $('#select_account').children();
    old_options.slice(1, old_options.length).remove();
}
    
// Fills out the accounts combobox if accounts are available for the
// current hostname
function fill_out_accounts(hostname)
{
    clear_accounts()
    if (account_table.hasOwnProperty(hostname)) {
        Object.keys(account_table[hostname]).forEach(function(account){
            $('#select_account').append(
                $('<option>', {value: account, text : account}))
        })
    }
    // Select the given username_guess if it's in the accounts list
    // else we'll just take the first account we know
    if (account_table.hasOwnProperty(hostname)) {
        if (username_guess in account_table[hostname]) {
            $('#input_account').val(username_guess);
        } else {
            var first_hostname = Object.keys(account_table[hostname])[0];
            $('#input_account').val(first_hostname);   
        }
    }
    // We might have to set password settings for the selected hostname + account
    update_password_settings();
}

// Activate the interface after everything has been initialized properly
function activate_gui(hostname, username_guess) {    
    // Set the current hostname in the hostname / url field
    $('#input_hostname').val(hostname);
    
    // Activate all inputs
    $('.gui_disabled_default').prop('disabled', false);
    
    fill_out_accounts(hostname);
    
    // Set the 'Save info' checkbox only if it says so in the extensions
    // settings
    chrome.storage.sync.get(['save_info'], function(result) {
        $('#checkbox_save_info').prop('checked', result.save_info);
    });
}

// Advanced settings menu show/hide function
function init_advanced_settings_gui() {
    $('.collapsible').click(function() {
        if($('.hidden_content').css('display') == 'none') {
            dbg_message('SHOW HIDDEN');
            $('.hidden_content').css('display', 'inline-block');
        }
        else {
            $('.hidden_content').css('display', 'none');
        }
    });
}

// Handler for messages from the background script
function background_port_message_handler(message) {
    dbg_message('Background -> Menu: ' + JSON.stringify(message));
    
    switch (message.cmd) {    
        case 'check_device_available':
            if (message.msg == 'True') {
                $('#device_not_connected_notice').hide();
                $('#form').show();
                get_options();
            }
            break;

        case 'request_pin':
            set_pin(message.msg);
            get_account_table();
            break;
            
        case 'get_account_table':
            account_table = message.msg
            request_website_info();
            break;
            
        case 'add_new_entry':
            send_request();
            break;        
    }
}

// Handler for messages from the content script
function content_port_message_handler(message) {
    dbg_message('Content -> Menu: ' + JSON.stringify(message));
    
    switch (message.cmd) {
        case 'error':
            window.alert(message.msg);
            window.close();
            break;
        
        case 'website_info':
            hostname = (message.msg['hostname']);
            username_guess = message.msg['username'];
            activate_gui(hostname, username_guess)
            break;
    }
}

// Ask if the device is plugged in
function ask_device_plugged_in() {
    background_port.postMessage({cmd: 'check_device_available'});
}

// Get the current options
function get_options() {
    // Set to automatically hit enter if selected in settings
    chrome.storage.sync.get({
        'save_info': true,
        'save_pin_active_session': true,
        'hit_enter': false},
        function(items) {
            options = items;
            // Continue init process by asking bg script for pin
            // after we received our options
            ask_for_pin();
        });
}

// Ask the background script for the pin
function ask_for_pin() {
    background_port.postMessage({cmd: 'request_pin'});
}

// Set the pin field with the value we obtained from the background script
// and continue with the init phase
function set_pin(pin)
{
    $('#input_pin').val(pin);
    
    // Continue initialization
    request_website_info();
}

// Ask the background script for the account table
function get_account_table() {
    background_port.postMessage({cmd: 'get_account_table'});
}

// Get current hostname and possible username from content script
function request_website_info() {
    // We eventually initialize the content port here
    // But we don't want to wait for our content script if the user clicks
    // on the button faster than the webpage loading time we'll just
    // skip the content script part
    if (content_port) {
        content_port.onMessage.addListener(content_port_message_handler);
        content_port.postMessage({cmd: 'website_info'});
    }
    else {
        activate_gui('', '');
    }
}

// Read the input fields and build a JSON message
function gui_input_to_request() {
    return {
        'hostname': $('#input_hostname').val(),
        'account': $('#input_account').val(),
        'pin': $('#input_pin').val(),
        'password_iteration': $('#password_iteration').val(),
        'password_length': $('#password_length').val()
    }
}

// Send the password request to the device
function send_request()
{
    request = gui_input_to_request();
    request['hit_enter'] = options.hit_enter;
    request['save_new_info'] = check_new_info_save();
    // And then the request for the usb device    
    background_port.postMessage({cmd: 'request_password', msg: request});
    
    // Refocus on the password field on the website
    if (content_port) {
        content_port.postMessage({cmd: 'refocus'});
    }
    
    window.close();
}

// Entry point of menu script
$(document).ready(function() {
    dbg_message('started');
    init_advanced_settings_gui();
    
    
    background_port.onMessage.addListener(background_port_message_handler);
    
    // Init gui events
    init_gui_change_events();
    
    // Start the initialization
    ask_device_plugged_in()
    
    // Bind the submit event to a password request
    $('#form').submit(send_request);
});
