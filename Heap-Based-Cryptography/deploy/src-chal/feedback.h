#ifndef FEEDBACK_H
#define FEEDBACK_H

#include "chal.h"
#include "crypto.h"

#define MAX_AUTHOR_LEN 10

typedef struct Feedback {
    char author[MAX_AUTHOR_LEN];
    char *feedback;
    size_t feedback_len;
    bool has_been_edited;
} feedback_t;

feedback_t *open_feedback(void);
int check_for_changes(feedback_t *fb);
void submit_feedback(feedback_t *fb, uint8_t *sk);
void edit_feedback(feedback_t *fb);
void close_feedback(feedback_t *fb);
uint8_t *create_ticket(size_t *ticket_len, feedback_t *fb);

#endif
