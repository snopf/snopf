// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

// Gui elements
check_save_info = document.getElementById('save_info');

check_save_pin_active_sessions = document.getElementById(
    'save_pin_active_session');

check_hit_enter = document.getElementById('hit_enter')

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
        save_info: check_save_info.checked,
        save_pin_active_session: check_save_pin_active_sessions.checked,
        hit_enter: check_hit_enter.checked
    }, show_saved_message);
}

// Set the GUI elements corresponding to the loaded options
function set_current_choice(items)
{
    check_save_info.checked = items.save_info;
    check_save_pin_active_sessions.checked = items.save_pin_active_session;
    hit_enter: check_hit_enter.checked = items.hit_enter;
}

// Restore the options from the HDD
function restore_options() {
    chrome.storage.sync.get({
        'save_info': true,
        'save_pin_active_session': true,
        'hit_enter': false},
        set_current_choice);
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
                                                 save_options);
