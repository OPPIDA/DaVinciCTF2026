#ifndef CHAL_H
#define CHAL_H

#include <stdlib.h>
#include <stdio.h>
#include <sys/random.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <arpa/inet.h>

#include "feedback.h"
#include "crypto.h"

#define FLAG "DVCTF{send write-up to wu-ctf@oppida.fr}"

void claim_flag(void);
void flush(void);

#endif
