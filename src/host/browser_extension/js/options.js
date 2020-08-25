// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

// Gui elements
check_add_new_entries = document.getElementById('add-new-entries');
check_hit_enter = document.getElementById('hit-enter');
websocket_port_input = document.getElementById('websocket-port');
websocket_id_input = document.getElementById('websocket-id');

// Show a 'Options saved' message
function show_saved_message()
{
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(function() {
        status.textContent = '';
    }, 750);
}

// Save the options
function save_options()
{
    chrome.storage.sync.set({
        add_new_entries: check_add_new_entries.checked,
        hit_enter: check_hit_enter.checked,
        websocket_port: websocket_port_input.value,
        websocket_id: websocket_id_input.value
    }, show_saved_message);
}

// Set the GUI elements corresponding to the loaded options
function set_current_choice(items)
{
    check_add_new_entries.checked = items.add_new_entries;
    check_hit_enter.checked = items.add_new_entries;
    websocket_port_input.value = items.websocket_port;
    if (items.websocket_id == null) {
        // Create new ID
        items.websocket_id = get_id()
        // Store the new id, else a new ID would be created until the user clicked 'save' once
        chrome.storage.sync.set({websocket_id: items.websocket_id});
    }
    websocket_id_input.value = items.websocket_id;
}

// Get a new random 12 digit ID
function get_id()
{
    x = new Uint8Array(9);
    crypto.getRandomValues(x);
    return btoa(String.fromCharCode.apply(null, x));
}

// Restore the options from the HDD, set default values if no options set
function restore_options() {
    chrome.storage.sync.get({
        'add_new_entries': true,
        'hit_enter': false,
        'websocket_port': 60100,
        'websocket_id': null},
        set_current_choice);
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);


document.getElementById('origin-header').value = window.origin
