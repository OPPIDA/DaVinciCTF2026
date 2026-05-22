#include "chal.h"

void print_header(void)
{
    printf(
    "      )                           \n"
    "   ( /(                 (         \n"
    "   )\\())            (   )\\ )   )  \n"
    "  ((_ )\\  `  )  `  ) )\\ (()/(( /(  \n"
    "    ((_) /(/(  /(/(((_) ((_))(_)) \n"
    "   / _ \\((_)_\\((_)_\\(_) _| ((_)_  \n"
    "  | (_) | '_ \\) '_ \\) / _` / _` | \n"
    "   \\___/| .__/| .__/|_\\__,_\\__,_| \n"
    "        |_|   |_|                 \n"
    );
    printf("  *(Challenge by skilo @ Oppida.)*\n");
    printf("\n");
}

void print_menu(void)
{
    printf("*** Liste des options disponibles ***\n");
    printf("*0* Ouvrir un feedback\n");
    printf("*1* Modifier un feedback\n");
    printf("*2* Fermer un feedback\n");
    printf("*3* Envoyer un feedback\n");
    printf("*4* Claim flag\n");
    printf("*5* Quitter\n");
    printf("\n> ");
}

void flush(void)
{
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

int main(void)
{
    int choice = 5;
    feedback_t *fb = NULL;

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin , NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    print_header();

    if (init_crypto() != 0)
    {
        printf("Error while generating keys.\n");
        exit(1);
    }

    uint8_t *sk = get_sk();

    for (int call = 0; call < 20; call++)
    {
        print_menu();

        if (1 != scanf("%d", &choice))
            exit(1);

        flush();

        switch (choice)
        {
            case 0:
                fb = open_feedback();
                break;

            case 1:
                edit_feedback(fb);
                break;

            case 2:
                close_feedback(fb);
                fb = NULL;
                break;

            case 3:
                submit_feedback(fb, sk);
                break;

            case 4:
                claim_flag();
                break;

            case 5:
                if (free_crypto(sk) != true)
                    continue;

                if (check_for_changes(fb) == true)
                    continue;

                printf("A la prochaine :=)\n");
                exit(EXIT_SUCCESS);

            default:
                printf("Invalid choice.\n");
                exit(EXIT_FAILURE);
        }
    }
}
