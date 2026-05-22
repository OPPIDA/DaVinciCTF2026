#include "feedback.h"

feedback_t *open_feedback(void)
{
    char author[MAX_AUTHOR_LEN] = {0};
    printf("Quel est ton prénom ? ");
    if (fgets(author, MAX_AUTHOR_LEN, stdin) == NULL)
    {
        printf("Error while reading your name :(\n");
        exit(1);
    }
    author[strcspn(author, "\n")] = '\0';
    size_t feedback_len = 0;
    printf("Quelle est la longueur de ton feedback ? ");
    scanf("%zu", &feedback_len);

    if (feedback_len > 0x1000 || feedback_len == 0)
    {
        printf("On le lira pas...\n");
        exit(1);
    }

    feedback_t *fb = malloc(sizeof(feedback_t));
    fb->feedback = malloc(feedback_len);
    fb->feedback_len = feedback_len;
    fb->has_been_edited = false;
    memcpy(fb->author, author, MAX_AUTHOR_LEN);
    printf("[*] Le feedback à été ouvert avec succès.\n");

    return fb;
}

int check_for_changes(feedback_t *fb)
{
    if (fb == NULL)
        return 0;

    if (fb->has_been_edited)
    {
        char res;
        printf("Are you sure to leave without sending your feedback ? (y/n)\n");
        printf("> ");

        scanf("%c", &res);

        if (res == 'n')
            return 1;
    }

    return 0;
}

void submit_feedback(feedback_t *fb, uint8_t *sk)
{
    if (fb == NULL)
    {
        printf("Please open a feedback first.\n");
        return;
    }

    // We don't care about your feedback
    FILE *f = fopen("/dev/null", "w");
    if (f) {
        fputs(fb->feedback, f);
        fclose(f);
    }

    // Generating ticket
    size_t ticket_len = 0;
    uint8_t *ticket = create_ticket(&ticket_len, fb);
    size_t ticket_sig_len = SIG_SIZE;
    uint8_t *ticket_sig = sign(sk, ticket, ticket_len);

    printf("Merci pour ton feedback :)\n");
    printf("Voici ton accusé de reception : ");
    for(int i = 0; i < ticket_len; i++) printf("%02x", ticket[i]);
    printf(";");
    for(int i = 0; i < ticket_sig_len; i++) printf("%02x", ticket_sig[i]);
    printf("\n");

    close_feedback(fb);
    return;
}

void edit_feedback(feedback_t *fb)
{
    if (fb == NULL)
    {
        printf("Merci d'ouvrir un feedback d'abord.\n");
        return;
    }

    size_t feedback_len = fb->feedback_len;
    uint8_t *buf = (uint8_t*)malloc(feedback_len + 1);

    printf("Contenu du feedback : ");
    if (fgets(buf, feedback_len, stdin) == NULL)
    {
        printf("Error while reading your name :(\n");
        free(buf);
        exit(1);
    }

    uint8_t *p = memchr(buf, '\n', feedback_len);
    size_t buf_end = p ? (size_t)(p - buf) : feedback_len;
    memcpy(fb->feedback, buf, buf_end);
    fb->has_been_edited = true;
    free(buf);
}

void close_feedback(feedback_t *fb)
{
    if (fb == NULL)
    {
        printf("Merci d'ouvrir un feedback d'abord.\n");
        return;
    }

    free(fb->feedback);
    free(fb);
}

uint8_t *create_ticket(size_t *ticket_len, feedback_t *fb)
{
    *ticket_len = MAX_AUTHOR_LEN + sizeof(void*);
    uint8_t *ticket = malloc(*ticket_len);
    uint8_t *p = ticket;
    memcpy(p, fb->author, MAX_AUTHOR_LEN);
    p += MAX_AUTHOR_LEN;
    memcpy(p, &fb->feedback, sizeof(void*));

    return ticket;
}
