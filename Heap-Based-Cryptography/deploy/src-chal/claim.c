#include "chal.h"

void claim_flag(void)
{
    char *magic = "I love Hash-based cryptography!";
    size_t magic_len = strlen(magic);

    uint8_t *pk = get_pk();
    uint8_t *sig = malloc(SIG_SIZE+1);
    printf("sig = ");
    if (fread(sig, 1, SIG_SIZE+1, stdin) != SIG_SIZE+1)
        exit(1);

    // Verify signature
    bool res = hss_validate_signature(
        pk, magic, magic_len, sig, SIG_SIZE, 0
    );

    if (res)
    {
        printf("Youhouuu : %s\n", FLAG);
        exit(0x45);
    }
    else
        exit(1);
}
