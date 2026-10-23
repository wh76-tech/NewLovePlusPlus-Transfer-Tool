import struct
import shutil
import os
import keystone
import capstone

ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_ARM)
cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)

patches_def = [
    # Patch 1: CardSlotIsInserted always returns 1
    (0x002d315c, '''
        mov r0, #1
        bx lr
    ''', "CardSlotIsInserted"),

    # Patch 2: Thread card detection callback populates LovePlus+
    (0x0036d0e8, '''
        cmp r1, #0
        moveq r0, #1
        bxeq lr
        mov r0, #4
        strb r0, [r1]
        mov r0, #1
        strb r0, [r1, #0xd]
        strb r0, [r1, #0xe]
        mov r0, #0
        str r0, [r1, #0x10]
        mov r0, #0x40000
        str r0, [r1, #0x14]
        mov r0, #1
        bx lr
    ''', "Thread card detect"),

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

    # Patch 5: SDMC loader cave at 0x003d61b0
    (0x003d61b0, '''
        push {r4, r5, r6, lr}
        sub sp, sp, #0x30

        mov r4, r0
        mov r0, #4
        strb r0, [r4, #0x50]
        mov r0, #1
        strb r0, [r4, #0x5d]
        strb r0, [r4, #0x5e]
        mov r0, #0
        str r0, [r4, #0x60]
        mov r0, #0x40000
        str r0, [r4, #0x64]

        ldr r5, [r4, #0x78]

        mov r0, #1
        str r0, [sp]
        mov r0, #0
        str r0, [sp, #4]
        str r0, [sp, #8]
        mov r0, #3
        str r0, [sp, #0xc]
        adr r0, path_str
        str r0, [sp, #0x10]
        mov r0, #9
        str r0, [sp, #0x14]
        mov r0, #1
        str r0, [sp, #0x18]
        mov r0, #0
        str r0, [sp, #0x1c]

        ldr r0, fs_hnd_ptr
        add r1, sp, #0x20
        mov r2, #0
        mov r3, #9

        bl 0x002b9484

        cmp r0, #0
        bne cleanup_exit

        add r0, sp, #0x20
        add r1, sp, #0x24
        mov r2, #0
        mov r3, #0
        str r5, [sp]
        mov r6, #0x40000
        str r6, [sp, #4]

        bl 0x00260cd0
        mov r4, r0

        ldr r0, [sp, #0x20]
        svc 0x23

        mov r0, r4

    cleanup_exit:
        add sp, sp, #0x30
        pop {r4, r5, r6, pc}

        .align 2
    fs_hnd_ptr:
        .word 0x0046a7c0
    path_str:
        .asciz "/lpp.sav"
    ''', "SDMC loader cave")
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

# 2. Patch original exefs/code.bin to produce a directly patched code.bin
with open('exefs/code.bin', 'rb') as f:
    orig_code = bytearray(f.read())

for offset, code, desc in compiled_patches:
    orig_code[offset:offset+len(code)] = code

with open('code_patched.bin', 'wb') as f:
    f.write(orig_code)
print(f'Wrote code_patched.bin ({len(orig_code)} bytes)')

# 3. Deploy to Azahar mod directory
azahar_mod_dir = r'C:\Users\weiha\AppData\Roaming\Azahar\load\mods\0004000000120D00\exefs'
os.makedirs(azahar_mod_dir, exist_ok=True)

shutil.copy('code.ips', os.path.join(azahar_mod_dir, 'code.ips'))
shutil.copy('code_patched.bin', os.path.join(azahar_mod_dir, 'code.bin'))
print(f'Copied code.ips and code.bin to {azahar_mod_dir}')

# 4. Verify sdmc/lpp.sav exists
azahar_sdmc_sav = r'C:\Users\weiha\AppData\Roaming\Azahar\sdmc\lpp.sav'
if not os.path.exists(azahar_sdmc_sav):
    shutil.copy('lpp.sav', azahar_sdmc_sav)
    print(f'Copied lpp.sav to {azahar_sdmc_sav}')
else:
    print(f'lpp.sav already present in {azahar_sdmc_sav} ({os.path.getsize(azahar_sdmc_sav)} bytes)')
