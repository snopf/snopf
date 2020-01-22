// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)


// Content script to retain password and possible username field from the
// current DOM


function dbg_message(msg)
{
    console.log('SNOPF_CONTENT: ' + msg);
}

var debugging = false;

// Guess for the password field, we'll store this to refocus later
var password_field = null;

// Guess for the username on the current website
var username = '';

// Current hostname
var hostname = '';

// Sanitize the intial hostname to something like bla.com
// TODO is there a smarter way to do this?
function sanitize_hostname(hostname) {
    split_hostname = hostname.split('.');
    
    if (split_hostname.length <= 2) {
        // The last part should always be .com etc.
        return hostname;
    }
    split_hostname = split_hostname.slice(
        split_hostname.length-2, split_hostname.length);
        
    return split_hostname.join('.');    
}

// Try to get the current url and guesses for hostname and the password field
function find_website_info()
{
    // Find hostname
    var url = new URL(window.location.href);
    hostname = sanitize_hostname(url.hostname)
    // try to guess username and password field
    guess_username();
    guess_password_field();
}

// Returns the first match that can be found by using the given
// jquery selectors
function first_match(selectors)
{
    var match = null;
    var matches = [];
    var i;
    for(i = 0; i < selectors.length; i++) {
        matches = $('input'+selectors[i]);
        if(matches.length > 0) {
            match = matches.first();
            break;
        }
    }
    return match;
}

// Get the first guess for the password field
function guess_password_field()
{
    // Possible password field selectors
    var password_selectors = [
                                '[type="password"]', 
                                '[name="password"]',
                                '[name="passwd"]',
                                '[autocomplete="current-password"]',
                                '[autocomplete="new-password"]'
                            ];
    password_field = first_match(password_selectors);
    if (password_field && debugging) {
        password_field.css('background-color', 'red');
    }
}

// Get the first guess for the username
function guess_username()
{
    // Some possible selectors to find the username input
    var username_selectors = [
                                '[autocomplete="username"]',
                                '[name="user"]',
                                '[name="username"]',
                                '[id="loginUsername]',
                                '[placeholder="username"]', 
                                '[placeholder="Username or email"]',
                                '[id="name"]',
                                '[name="name"]',
                                '[name="login"]',
                                '[id="email"]',
                                '[name="email"]',
                                '[name="f.loginName"]'
                            ];
    
    username_field = first_match(username_selectors);
    
    if (username_field && debugging) {
        username_field.css('background-color', 'green');
    }
    if (username_field) {
        username = username_field.val();
    }
}


// We'll want to put the focus on the password field after we left the
// extensions menu so the user just has to press the button on the device
function refocus_password_field()
{
    if (password_field) {
        dbg_message('Refocus password field.');
        password_field.focus();
    }
}

// Handle the requests from the extension
function message_handler(msg)
{
    dbg_message('Menu -> Content: ' + JSON.stringify(msg));
    if (msg.cmd == 'website_info') {
        port.postMessage(
            {cmd: 'website_info',
             msg: {hostname: hostname, username: username}});
    } 
    else if (msg.cmd == 'refocus') {
        refocus_password_field();
    }
}

var port;
function connected(p) {
    port = p;
    port.onMessage.addListener(message_handler);
}
chrome.runtime.onConnect.addListener(connected);

find_website_info();

dbg_message('Ready');
