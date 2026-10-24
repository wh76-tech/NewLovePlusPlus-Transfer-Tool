import struct
import shutil
import os
import keystone
import capstone

ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_ARM)
cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)

cave_asm = """
    push {r4, r5, r6, r7, lr}
    sub sp, sp, #0x38

    mov r4, r0                 @ r4 = context pointer

    @ Setup FS open parameters on stack
    mov r0, #1
    str r0, [sp]
    mov r0, #0
    str r0, [sp, #4]
    str r0, [sp, #8]
    mov r0, #3
    str r0, [sp, #0xc]
    mov r0, #9
    str r0, [sp, #0x14]
    mov r0, #1
    str r0, [sp, #0x18]
    mov r0, #0
    str r0, [sp, #0x1c]

    @ Try open /lpp.sav first
    adr r0, path_lpp
    str r0, [sp, #0x10]
    ldr r0, fs_hnd_ptr
    add r1, sp, #0x20
    mov r2, #0
    mov r3, #9
    bl 0x002b9484              @ FSUSER_OpenFileDirectly(/lpp.sav)

    cmp r0, #0
    beq file_opened

    @ If /lpp.sav failed, try /lp.sav
    adr r0, path_lp
    str r0, [sp, #0x10]
    ldr r0, fs_hnd_ptr
    add r1, sp, #0x20
    mov r2, #0
    mov r3, #9
    bl 0x002b9484              @ FSUSER_OpenFileDirectly(/lp.sav)

    cmp r0, #0
    bne cleanup_exit

file_opened:
    @ Get File Size: FSFILE_GetSize
    mrc p15, 0, r0, c13, c0, 3  @ get TLS
    add r0, r0, #0x80           @ cmdbuf
    mov r1, #0x08000000
    orr r1, r1, #0x00010000     @ 0x08010000
    str r1, [r0]
    ldr r0, [sp, #0x20]         @ file handle
    svc 0x32                    @ SendSyncRequest
    mrc p15, 0, r0, c13, c0, 3
    add r0, r0, #0x80
    ldr r2, [r0, #8]            @ file size (low 32 bits)

    @ Check if size <= 0x10000 (64KB -> LovePlus 1)
    mov r1, #0x10000
    cmp r2, r1
    ble is_lp

is_lpp:
    mov r7, #4                  @ type_id = 4 (LovePlus+)
    mov r6, #0x40000            @ size = 0x40000 (256KB)
    b fill_meta

is_lp:
    mov r7, #2                  @ type_id = 2 (LovePlus 1)
    mov r6, #0x10000            @ size = 0x10000 (64KB)

fill_meta:
    strb r7, [r4, #0x50]        @ context type_id (2 or 4)
    mov r0, #1
    strb r0, [r4, #0x5d]
    strb r0, [r4, #0x5e]
    mov r0, #0
    str r0, [r4, #0x60]
    str r6, [r4, #0x64]        @ context save_size (0x10000 or 0x40000)

    @ Update global detected vars in cave
    adr r0, global_type
    str r7, [r0]
    adr r0, global_size
    str r6, [r0]

    @ Read file into context buffer: [r4, #0x78]
    ldr r5, [r4, #0x78]
    add r0, sp, #0x20           @ &fileHandle
    add r1, sp, #0x24           @ &bytesRead
    mov r2, #0                  @ offset low = 0
    mov r3, #0                  @ offset high = 0
    str r5, [sp]                @ buffer
    str r6, [sp, #4]            @ size = r6!

    bl 0x00260cd0               @ FSFILE_Read

    mov r4, r0                  @ save result

    @ Close file handle
    ldr r0, [sp, #0x20]
    svc 0x23                    @ svcCloseHandle

    mov r0, r4                  @ return result

cleanup_exit:
    add sp, sp, #0x38
    pop {r4, r5, r6, r7, pc}

    .align 2
fs_hnd_ptr:
    .word 0x0046a7c0
global_type:
    .word 4
global_size:
    .word 0x40000
    .align 2
path_lpp:
    .asciz "/lpp.sav"
    .align 2
path_lp:
    .asciz "/lp.sav"
"""

patch2_asm = """
    cmp r1, #0
    moveq r0, #1
    bxeq lr
    ldr r0, =0x003d62e8
    ldr r2, [r0]
    strb r2, [r1]
    mov r0, #1
    strb r0, [r1, #0xd]
    strb r0, [r1, #0xe]
    mov r0, #0
    str r0, [r1, #0x10]
    ldr r0, =0x003d62ec
    ldr r2, [r0]
    str r2, [r1, #0x14]
    mov r0, #1
    bx lr
"""

patches_def = [
    # Patch 1: CardSlotIsInserted always returns 1
    (0x002d315c, '''
        mov r0, #1
        bx lr
    ''', "CardSlotIsInserted"),

    # Patch 2: Thread card detection callback reads dynamic global_type/global_size
    (0x0036d0e8, patch2_asm, "Thread card detect"),

    # Patch 3: Title State 1 jumps straight to State 4
    (0x0036ed54, '''
        mov r0, #4
        str r0, [r4, #0x70]
        b 0x0036ee60
        nop
        nop
    ''', "State 1 bypass to State 4"),

    # Patch 4: Hook ReadSaveDataFromCard to SDMC cave
    (0x0037022c, '''
        b 0x003d61b0
    ''', "Hook ReadSaveDataFromCard"),

    # Patch 5: Universal SDMC loader cave (supports both LovePlus 1 & LovePlus+)
    (0x003d61b0, cave_asm, "Universal SDMC loader cave")
]

base = 0x00100000
compiled_patches = []

for addr, code_str, desc in patches_def:
    code_bytes, _ = ks.asm(code_str, addr)
    b = bytes(code_bytes)
    if len(b) % 4 != 0:
        b += bytes(4 - (len(b) % 4))
    offset = addr - base
    compiled_patches.append((offset, b, desc))
    print(f'[{desc}] offset=0x{offset:06x}, len={len(b)}')

# 1. Build code.ips
ips_data = bytearray(b'PATCH')
for offset, code, desc in compiled_patches:
    assert offset < 0x1000000, f'Offset 0x{offset:x} exceeds 24-bit IPS limit'
    assert len(code) <= 0xFFFF, f'Size {len(code)} exceeds 16-bit IPS record limit'
    ips_data.append((offset >> 16) & 0xFF)
    ips_data.append((offset >> 8) & 0xFF)
    ips_data.append(offset & 0xFF)
    ips_data.append((len(code) >> 8) & 0xFF)
    ips_data.append(len(code) & 0xFF)
    ips_data.extend(code)

ips_data.extend(b'EOF')

with open('code.ips', 'wb') as f:
    f.write(ips_data)
print(f'Wrote code.ips ({len(ips_data)} bytes)')
print('Embedded code.ips hex string:')
print(ips_data.hex())

if os.path.exists('exefs/code.bin'):
    with open('exefs/code.bin', 'rb') as f:
        patched_bin = bytearray(f.read())
    for offset, code, desc in compiled_patches:
        patched_bin[offset : offset + len(code)] = code
    with open('code_patched.bin', 'wb') as f:
        f.write(patched_bin)
    print('Updated code_patched.bin successfully!')
