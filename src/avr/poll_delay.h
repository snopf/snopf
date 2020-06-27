// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __poll_delay_h__
#define __poll_delay_h__

#include <stdint.h>

// Idle for the given number of milliseconds and call usbPoll regularly
void poll_delay_ms(uint16_t ms);

#endif
