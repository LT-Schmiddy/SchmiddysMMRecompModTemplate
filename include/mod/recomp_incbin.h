#ifndef __RECOMP_INCBIN__
#define __RECOMP_INCBIN__


#ifdef RECOMP_INCBIN_EXTERN_ONLY
#define RECOMP_INCBIN(identifier, filename)           \
    extern u8 identifier[];                           \
    extern u8 identifier##_end[]

#else
#define RECOMP_INCBIN(identifier, filename)           \
    asm(".pushsection .rodata\n"                      \
        "\t.globl " #identifier "\n"                  \
        "\t.type " #identifier ", @object\n"          \
        "\t.balign 8\n"                               \
        #identifier ":\n"                             \
        "\t.incbin \"" filename "\"\n"                \
        "\t.globl " #identifier "_end\n"              \
        #identifier "_end:\n"                         \
        "\t.popsection\n");                           \
    extern u8 identifier[];                           \
    extern u8 identifier##_end[]
#endif
#endif