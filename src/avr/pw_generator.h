// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __pw_generator_h__
#define __pw_generator_h__

#include <stdint.h>

// Tools for generating and sending a password to the host device

// Process the current password request using the given EEPROM secret
void pw_process_request(const uint8_t* secret);

#endif
