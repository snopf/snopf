// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __secret_change_h__
#define __secret_change_h__

#include <stdint.h>

/*
 * Definitions of the secret changing routines.
 */

// Returns 1 if we are currently in a secret changing routine, else 0
// Also advances one step in the secret change routine if the return value
// is 1
uint8_t csecret_check_state(void);

#endif  //__secret_change_h__
