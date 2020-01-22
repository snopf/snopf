// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "poll_delay.h"
#include "usbdrv.h"
#include <util/delay.h>

void poll_delay_ms(uint16_t ms)
{
    for (uint16_t i = 0; i < ms; i++) {
        if (i % 20 == 0) {
            usbPoll();
        }
        _delay_ms(1);
    }
}
