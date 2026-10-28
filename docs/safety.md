# Safety: radios, delivery, locks and the way back

Read this before any work that could reach a radio. It expands the hard rules in [AGENTS.md](../AGENTS.md). Upstream facts are cited
as `upstream/<path>`, at the commit pinned in `upstream/` ([upstream.md](upstream.md)).

## 1. Approval for every radio action

| Action | Needs | Recorded where |
|---|---|---|
| Read-only CAT queries (`ID;`, `VE0;`, `tools/cat_backup.py` in upstream) | the owner's go-ahead in the session | the project page's test log |
| Any write: SD-card update, CAT set-command, EEPROM write, JTAG/SWD load, opening the radio | the owner's **explicit approval for that specific action, each time** | the project page's test log (date, what was approved, by whom) |
| Transmitting with modified firmware | approval, plus a dummy load for the first tests | the project page's test log |

Approval for one write never covers the next one, a different image or a different radio.

## 2. Backups

Before the first write to a radio, back it up and keep the files off the radio:

1. **SD card (Yaesu's method):** memories and menus. Steps: `upstream/docs/cat-undocumented.md` §2.1.
2. **CAT backup, including the full EEPROM** (the only backup of the factory calibration):
   `python3 -I upstream/tools/cat_backup.py <port> <dir> --eeprom`. It sends only reads, logs to `backup.log`, writes `SHA256SUMS`, and
   `--verify <dir>` checks it later. Details: `upstream/docs/cat-undocumented.md` §2.2–2.4.
3. **Firmware versions** (`VE0;`..`VE3;`, in `info.txt`) and the factory `.SFL` files of exactly those versions, so stock can be put back.

Record the backup folder's `SHA256SUMS` hash in the test log.

## 3. Delivery and the way back to stock

Hard rule 4: **every custom image is an ordinary `.SFL` update file that the radio's own SD-card update installs, and installing a
factory `.SFL` always restores stock.**

### 3.1 How the stock update works (upstream facts)

From `upstream/docs/code/display/update.md` §1 and `upstream/docs/custom-firmware.md`:

- The DISPLAY CPU runs every update from the SD card (menu **SD CARD → FIRMWARE UPDATE**): itself (SPI-flash banks), MAIN (RX651
  serial boot mode), IFDSP (RT685 ROM ISP through MAIN) and the SDR FPGA (configuration flash, through MAIN and the DISPLAY SDR SPI)
  **[fact]**.
- A file is taken from `I:\FT-710\`, named `FT-710_<IMG>_V` + 4 characters + `.sfl`; when several match, **the lexicographically
  highest name wins**; the 4 characters are shown as the version **[fact]**.
- The only content check is the salted CRC-32 in the SFL header. There is no signature, model, destination or serial check
  **[fact]**. Downgrades are allowed: any "Ready" row can be ticked **[inference]**.
- Per image: MAIN S-records need valid record checksums and every area is read back and compared; the DISPLAY payload must decode
  to the right length; the IFDSP erase region is fixed at 0x08000000 + 0xA0000; the SDR file must be exactly 0x43075A bytes **[fact]**.
- DISPLAY updates itself by writing the **other** bank and switching the bank flag; boot prefers a valid bank 1 **[fact]**.

### 3.2 Requirements for every custom image

| # | Requirement | How it is checked |
|---|---|---|
| D1 | It is a valid `.SFL` that passes every check above, built from the official download by a committed script | `upstream/tools/sfl_encode.py --check FILE.SFL`, in the patch's test log |
| D2 | It is installed only through the standard SD-card update. No JTAG, SWD, serial-boot or loader-mode (`#UP0`) path is needed to install it | the project's install procedure |
| D3 | **The update path is untouched.** In a DISPLAY image: the update menu and file handling, `sfl_read_header`/`sfl_crc`, `fwobj_*_run`, `rx_boot_*`, `dsp_isp_*`, `sdr_flash_write`, `boot_select_bank` and the bank-flag code are byte-identical to stock. In MAIN: the code DISPLAY relies on to enter serial boot mode, and the status frame that reports versions, behave as in stock. In IFDSP and SDR: nothing that DISPLAY's programming routines depend on changes | a byte-compare of the listed functions (addresses from upstream) in the patch's test log |
| D4 | The image size stays within the stock limits (DISPLAY bank 6 MiB, IFDSP 640 KiB erase region, SDR exact size) | `sfl_encode.py --check` |
| D5 | **A factory file always wins.** A custom file's 4 version characters must sort **below** the factory version it is based on, so that if both files sit in `I:\FT-710\`, the update picks the factory file. The scheme is chosen per project and documented (open decision for the first project) | the file name in the test log |
| D6 | The install instructions say to keep only one file per image in `I:\FT-710\` | the project's install procedure |
| D7 | **Round trip before anything else:** the first radio test of any custom image ends by installing the factory `.SFL` of the base version and checking `VE0;`..`VE3;` and normal operation | the project's test log |
| D8 | Offline first: the image passes `--check`, the D3 byte-compare and (where possible) simulation or emulation before any radio test | the pull request |

### 3.3 If something goes wrong

| Situation | Path back |
|---|---|
| Custom image works but is unwanted | install the factory `.SFL` (D7) |
| DISPLAY does not boot after its update | it has two banks: the stock bank is still in flash; recovery is through the power-on maintenance/loader modes or JTAG (J6003). Document the exact steps in the project before the first DISPLAY test. See `upstream/docs/code/display/update.md` and `upstream/docs/custom-firmware.md` |
| MAIN does not start | DISPLAY can still put MAIN into serial boot mode and write the factory MAIN image from the SD card; JTAG/serial header J1004 as a last resort |
| IFDSP or SDR does not start | DISPLAY reprograms them from the factory files; SWD (J2009) or FPGA JTAG (J2001) as a last resort |
| Settings or calibration damaged | restore from the backups in section 2 |

Every project page must fill in its own version of this table before the first radio test.

## 4. Locks and option settings never change

Hard rule 5: **lock bits and option settings are never set or changed from stock.** Each custom image is compared with its stock base
in these areas, and the comparison is in the pull request.

| Chip | Area | Stock state (upstream facts) | Rule |
|---|---|---|---|
| MAIN RX651 | option-setting memory 0xFE7F5D00..0xFE7F5D73 (116 bytes, part of the MAIN `.SFL`) | all `0xFF`: little-endian, linear mode, no watchdog auto-start, serial programmer allowed with ID code 16 × `0xFF`, no access window, ROM code or Trusted Memory protection **[fact]** (`upstream/docs/memory-maps.md`) | the S-records for this area are byte-identical to stock, and no code writes the option-setting memory or the flash access window |
| MAIN RX651 | ID code (OSIS) | 16 × `0xFF` (the updater sends 16 × `0xFF`) **[fact]** | never changed; a changed ID code would lock out the standard update |
| IFDSP RT685 | OTP fuses, boot configuration, FlexSPI configuration block | OTP state unknown (needs an SWD read) **[fact]**; plain image boots from QSPI **[fact]** | no code programs OTP or eFuses; the boot header and FlexSPI configuration block are byte-identical to stock |
| DISPLAY RZ/A1H | SPI-flash protection, boot settings, security | no protection setting found in the code read so far **[inference]** | no code sets SPI-flash status/protection bits or changes boot settings |
| SDR Artix-7 | bitstream options, configuration-flash protection | uncompressed, unencrypted bitstream **[fact]** | no encryption, no readback/JTAG disable, no eFUSE or BBRAM key, no configuration-flash status-register or block-protection change; bitstream header options identical to stock except the logic itself |
| any chip | debug interfaces (JTAG/SWD) | open | never disabled |

If a project seems to need any of these changed, stop: that needs a separate owner decision in an issue, and the default answer is
no.

## 5. What is never committed

| Never | Instead |
|---|---|
| Yaesu's firmware download, `.SFL` files, decoded images (`build/` in upstream) | the official download URL and SHA-256 (upstream `docs/inputs.sha256`) |
| Patched images or patched `.SFL` files | the patch source (description, script, byte list) and the SHA-256 of the built output |
| Ghidra databases | names and scripts; Ghidra work belongs upstream |
| Radio backups (`eeprom.bin`, `e8_*.bin`) | their SHA-256 in the test log, if needed |

## 6. Licence and transmit

Transmit-path changes (band limits, power, filters, modes) must keep the radio within the operator's licence conditions (FCC Part 97
in the US). Test them into a dummy load first, and document the measurement.
