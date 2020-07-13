// Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "password_generator.h"

#include "sha256.h"
#include <string.h>

// Upper limits of inclusion rules
#define PW_GROUP_BOUND_1  18
#define PW_GROUP_BOUND_2  36
#define PW_GROUP_BOUND_3  46

void pw_gen_base64(uint8_t buffer[MAX_PW_LENGTH], const uint8_t seed[32],
                   uint8_t len)
{
    // We might encode more bits than necessary but this is a fast and
    // simple implementation and the buffer has to be large enough any way
    for (uint8_t i = 0; i < len; i++) {
        buffer[i] = *seed & 63;
        buffer[++i] = *seed >> 6;
        buffer[i] |= (*(++seed) << 2) & 63;        
        buffer[++i] = *seed >> 4;
        buffer[i] |= (*(++seed) << 4) & 63;
        buffer[++i] = (*(seed++) >> 2) & 63;
    }
}

int8_t pw_gen_replace_reps_and_seqs(uint8_t buffer[MAX_PW_LENGTH],
                                    const uint8_t keymap[64],
                                    uint8_t len, uint8_t rules)
{
    // We control the replacement of sequences and/or repeated characters
    // by adding offsets to the last character. We can use one function
    // for all three possible rule combinations this way
    uint8_t offset_1, offset_2;
    if ((rules & PW_GEN_NO_SEQ) && (rules & PW_GEN_NO_REP)) {
        offset_1 = 0;
        offset_2 = 1;
    } else if (rules & PW_GEN_NO_SEQ) {
        offset_1 = 1;
        offset_2 = 1;
    } else if (rules & PW_GEN_NO_REP) {
        offset_1 = 0;
        offset_2 = 0;
    } else {
        // Nothing to do
        return 1;
    }
    for (uint8_t i = 1; i < len; i++) {
        uint8_t k = 0;
        while ((keymap[buffer[i]] == keymap[buffer[i-1]] + offset_1)
            || (keymap[buffer[i]] == keymap[buffer[i-1]] + offset_2))
        {
            buffer[i]++;
            buffer[i] %= 64;
            if (++k == 64) {
                // We have to few keys to select from and can't apply
                // the rules
                return 0;
            }
        }
    }
    return 1;
}

int8_t pw_gen_check_inclusion_rules(const uint8_t buffer[MAX_PW_LENGTH],
                                    const uint8_t keymap[64],
                                    uint8_t len, uint8_t rules)
{
    for (uint8_t i = 0; i < len; i++) {
        if (keymap[buffer[i]] < PW_GROUP_BOUND_1) {
            rules &= ~PW_GEN_INCLUDE_GROUP_1;
        } else if (keymap[buffer[i]] < PW_GROUP_BOUND_2) {
            rules &= ~PW_GEN_INCLUDE_GROUP_2;
        } else if (keymap[buffer[i]] < PW_GROUP_BOUND_3) {
            rules &= ~PW_GEN_INCLUDE_GROUP_3;
        } else {
            rules &= ~PW_GEN_INCLUDE_GROUP_4;
        }
        if ((rules & PW_GEN_GROUP_RULES) == 0) {
            return 1;
        }
    }
    return 0;
}

void pw_gen_map_to_keymap(uint8_t buffer[MAX_PW_LENGTH],
                          const uint8_t keymap[64],
                          uint8_t len)
{
    for (uint8_t i = 0; i < len; i++) {
        buffer[i] = keymap[buffer[i]];
    }
}

uint8_t* pw_gen_generate_mapped(const uint8_t secret[32],
                               uint8_t message[16],
                               const uint8_t keymap[64],
                               uint8_t len, uint8_t rules)
{
    static uint8_t work_buffer[PW_BUFFER_SIZE];
    static uint8_t seed_buffer[32];
    uint8_t* result = NULL;
    
    if ((len <= MAX_PW_LENGTH) && (len >= MIN_PW_LENGTH)) {
        for (uint8_t i = 0; i < 0xff; i++) {
            sha256((uint32_t*)seed_buffer, (uint32_t*)secret,
                   (uint32_t*)message, (uint32_t*)work_buffer);
            
            pw_gen_base64(work_buffer, seed_buffer, len);
            
            // Apply all repeated / sequenced character rules
            if (!(pw_gen_replace_reps_and_seqs(work_buffer, keymap, len, rules))) {
                break;
            }
            
            // Check that the password is valid for the chosen inclusion rules
            if (pw_gen_check_inclusion_rules(work_buffer, keymap, len, rules)) {
                // If the password is ok, we map the base64 result to the keymap
                // indices
                pw_gen_map_to_keymap(work_buffer, keymap, len);
                result = work_buffer;
                break;
            }
            message[0]++;
        }
    }
    memset(seed_buffer, 0, 32);
    return result;
}
