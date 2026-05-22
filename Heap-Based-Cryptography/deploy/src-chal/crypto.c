#include "crypto.h"

param_set_t lm_type[D] = {
    LMS_SHA256_N32_H10,
    LMS_SHA256_N32_H15
};

param_set_t ots_type[D] = {
    LMOTS_SHA256_N32_W2,
    LMOTS_SHA256_N32_W8
};

uint8_t pubkey[PUBKEY_SIZE] = {0};
uint8_t privkey[PRIVKEY_SIZE] = {0};

bool rng(void *buf, size_t len)
{
    ssize_t res = getrandom(buf, len, 0);

    if ((size_t)res != len) {
        printf("Error while reading /dev/urandom.\n");
        exit(1);
    }

    return true;
}

bool free_crypto(uint8_t *sk)
{
    if (sk != NULL)
        free(sk);

    return true;
}

int init_crypto(void)
{
    if (!hss_generate_private_key(rng, D,
             lm_type, ots_type, NULL,
             privkey, pubkey, PUBKEY_SIZE,
             NULL, 0, 0)) {
        printf("Initial keygen attempt failed\n");
        return 1;
    }

    return 0;
}

uint8_t *sign(uint8_t *sk, uint8_t *buf, size_t buf_len)
{
    struct hss_working_key* w = hss_load_private_key(NULL, sk, 0, 0, 0, 0);
    if (w == NULL)
    {
        printf("Impossible de charger la clé privée ;(\n");
        exit(1);
    }

    uint8_t *sig = malloc(SIG_SIZE);
    struct hss_extra_info info = { 0 };
    bool success = hss_generate_signature(w, NULL, sk,
        buf, buf_len,
        sig, SIG_SIZE, &info);

    if(success)
        return sig;
    else
        return NULL;
}

uint8_t *get_pk(void)
{
    uint8_t* pk = (uint8_t*)malloc(PUBKEY_SIZE);
    if(pk == NULL)
    {
        printf("Erreur lors de l'allocation dynamique.\n");
        exit(1);
    }

    memcpy(pk, pubkey, PUBKEY_SIZE);
    return pk;
}

uint8_t *get_sk(void)
{
    uint8_t* sk = (uint8_t*)malloc(PRIVKEY_SIZE);
    if(sk == NULL)
    {
        printf("Erreur lors de l'allocation dynamique.\n");
        exit(1);
    }

    memcpy(sk, privkey, PRIVKEY_SIZE);
    return sk;
}

