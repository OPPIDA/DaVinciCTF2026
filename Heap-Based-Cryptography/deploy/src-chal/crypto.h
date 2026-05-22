#ifndef CRYPTO_H
#define CRYPTO_H

#include "chal.h"
#include "hss.h"

bool free_crypto(uint8_t *pk);
int init_crypto(void);
uint8_t *sign(uint8_t *sk, uint8_t *buf, size_t buf_len);
uint8_t *get_pk(void);
uint8_t *get_sk(void);

// Precomputed constants
#define D 2
#define PRIVKEY_SIZE 64
#define PUBKEY_SIZE  60
#define SIG_SIZE 6292
extern param_set_t lm_type[D];
extern param_set_t ots_type[D];
extern uint8_t pubkey[PUBKEY_SIZE];
extern uint8_t privkey[PRIVKEY_SIZE];

#endif
