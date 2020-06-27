// Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __password_generator_h__
#define __password_generator_h__

#include <stdint.h>

// Rules for group of characters that must be included
#define PW_GEN_GROUP_RULES 0xf
#define PW_GEN_INCLUDE_GROUP_1  (1 << 0)
#define PW_GEN_INCLUDE_GROUP_2  (1 << 1)
#define PW_GEN_INCLUDE_GROUP_3  (1 << 2)
#define PW_GEN_INCLUDE_GROUP_4  (1 << 3)

// Rules for avoiding repetitions and sequential characters
#define PW_GEN_NO_SEQ   (1 << 4)
#define PW_GEN_NO_REP   (1 << 5)

// Automatically hit enter after typing in the password
#define PW_GEN_HIT_ENTER    (1 << 6)

// Minimum length of a generated password
#define MIN_PW_LENGTH 6
// Maximum length of a generated password (32 bytes * 8 / 6)
#define MAX_PW_LENGTH 42

/*
 * Generate a base64 password combination for the given rules.
 * Returns 1 if a password could be generated, 0 else.
 */
int8_t pw_gen_generate_mapped(uint8_t work_buffer[256],
                              uint8_t seed_buffer[32],
                              const uint8_t secret[16],
                              uint8_t message[16],
                              const uint8_t keymap[64],
                              uint8_t len, uint8_t rules);

#endif  //__password_generator_h__
