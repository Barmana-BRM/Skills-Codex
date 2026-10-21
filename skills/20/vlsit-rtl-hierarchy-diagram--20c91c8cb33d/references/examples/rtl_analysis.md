# CAN Controller RTL Analysis (diagram level 1)

Companion of `rtl_hierarchy.drawio`. Skill: `vlsit-rtl-hierarchy-diagram`. Facts proven by RTL are cited as `file:line`; statements marked *Interpretation* are inferences.

## 1. Scope and evidence

- RTL root: `C:\HQuan\100_ForMe\013_Opencore\CAN\can\rtl\verilog` (13 files: 12 Verilog modules/headers listed below, `can_defines.v`, `README.txt`). No RTL file was modified.
- Selected diagram level N = 1 (user choice): level 0 = `can_top`; level 1 = the direct children of `can_top` and the functional groups of `can_top` own logic. Effective level = 1 (the hierarchy is deeper, see section 7).
- Top module: `can_top`. Evidence: `set_option -top_module "can_top"` in `syn/synplicity/can.prj:39`.
- Configuration assumption: delivered `can_defines.v` with no extra macros. `CAN_WISHBONE_IF` (`can_defines.v:100`), vendor RAM macros (`:103-113`), and `CAN_BIST` (`:116`) are commented out. Active host interface: 8051-style (`can_top.v:276-287`, `834-871`). The WISHBONE branch (`can_top.v:782-831`) is inactive and excluded.
- Evidence level: static RTL reading only. No compilation, simulation, or synthesis was run.
- Files inspected in detail: `can_top.v` (full), `can_btl.v` (ports, lines 155-481), `can_registers.v` (ports, 420-1255), `can_bsp.v` (ports and selected logic: 699-760, 1255-1440, 1590-1650, 1760-1840, 2008-2130), `can_register_asyn_syn.v`, `can_defines.v`, `README.txt`. Level-N modules are not analyzed below their ports and top-level behavior (RHD-013).

## 2. Hierarchy (levels 0-1)

| Depth | Instance | Module | File:line | Parent | Parameters | Notes |
|---|---|---|---|---|---|---|
| 0 | TOP | can_top | can_top.v:214 | - | `Tp = 1` | Own logic present; grouped into 3 functional groups (section 3a) |
| 1 | i_can_registers | can_registers | can_top.v:443 | TOP | none | Own logic present; **(not expanded; own logic)** |
| 1 | i_can_btl | can_btl | can_top.v:563 | TOP | none | Own logic present; **(not expanded; own logic)** |
| 1 | i_can_bsp | can_bsp | can_top.v:607 | TOP | none | Own logic present; **(not expanded; own logic)** |

Direct child modules of level-1 blocks (listed only, not analyzed):

| Level-1 block | Direct child modules |
|---|---|
| can_registers | can_register_asyn_syn, can_register_asyn, can_register (`can_registers.v:511-1069`) |
| can_btl | none |
| can_bsp | can_crc (`i_can_crc_rx`, :1260), can_acf (`i_can_acf`, :1275), can_fifo (`i_can_fifo`, :1398), can_ibo (15 instances, :1674-1690) |

`can_register_syn` is defined in `can_register_syn.v` but no instance of it was found in the RTL directory.

## 3. Module functions

| Module / block | Main function (from RTL) | Evidence |
|---|---|---|
| can_top | Integration level. Connects the three sub-blocks; implements the 8051-style host adapter, the host read-data multiplexer, and a two-stage synchronizer for `rx_i`. | `can_top.v:443-739`, `743-778`, `836-869` |
| i_can_registers (can_registers) | Host-visible register file: mode, command, status, interrupt enable, bus timing 0/1, error warning limit, clock divider, acceptance code/mask, 13 TX buffer bytes. Decodes host writes (`we_*` strobes), assembles the status register, generates seven interrupt sources and the latched active-low `irq_n`, multiplexes register reads, and derives the divided `clkout`. | `can_registers.v:444-486`, `502-700`, `715-855`, `1084-1142`, `1145-1251` |
| i_can_btl (can_btl) | CAN bit timing logic: baud-rate enable generation (`preset_cnt = (BRP+1)*2`), sync/seg1/seg2 segment machine with hard synchronization and resynchronization, optional triple sampling, generation of `sample_point` and `tx_point`. | `can_btl.v:257-445` |
| i_can_bsp (can_bsp) | CAN bit stream processor: receive state sequencing (idle, ID, RTR, IDE, DLC, data, CRC, ACK, EOF, intermission), bit de-stuffing, transmit bit selection and the registered `tx` output, arbitration-loss detection, error/overload frame control, error counters with error-passive and bus-off states, status flags, and, through children, CRC, acceptance filter and RX FIFO. | `can_bsp.v:699-721`, `1630-1646`, `1762-1840`, `2013-2127`; children at :1260, :1275, :1398 |

*Interpretation:* `can_registers` corresponds to an SJA1000-style register map (basic and extended mode selected by `extended_mode`, `can_registers.v:1093-1139`); the code itself does not name SJA1000.

### 3a. Functional groups of can_top own logic (RHD-080..085)

can_top own logic exists under the active configuration (inactive WISHBONE branch excluded). Three groups, within the limit of 10. Trivial renames `assign rst = rst_i; we = wr_i; addr = addr_latched; data_in = port_0_io` (`can_top.v:865-868`) are plain wiring and are not counted as logic. `initial` blocks: none.

| Module | Group | Function | Constructs and line ranges | State elements | Signals driven | Inputs | Outputs | Merge note |
|---|---|---|---|---|---|---|---|---|
| can_top | Host bus adapter | Latches the multiplexed address, detects write/read strobe edges, generates the one-cycle chip-select `cs`, and drives the bidirectional data port during reads. | `always` 837-843 (addr latch on `ale_i`), `always` 847-859 (`wr_i_q`, `rd_i_q`), `assign cs` 862, `assign port_0_io` 869 | `addr_latched[7:0]`, `wr_i_q`, `rd_i_q` | `cs`, `we`, `addr`, `data_in`, `rst`, `port_0_io` (read phase) | `ale_i`, `rd_i`, `wr_i`, `cs_can_i`, `rst_i`, `clk_i`, `port_0_io`, `data_out` | `cs`, `we`, `addr[7:0]`, `data_in[7:0]`, `rst`, `port_0_io` | none (3 groups) |
| can_top | Read-data select | Selects between register read data and RX-FIFO read data by address and mode, and registers the selected byte on a host read. | `always @(...)` 744-750 (`data_out_fifo_selected`), `always @(posedge clk_i)` 753-762 (`data_out`) | `data_out[7:0]` | `data_out_fifo_selected`, `data_out` | `extended_mode`, `reset_mode`, `addr`, `cs`, `we`, `data_out_regs`, `data_out_fifo` | `data_out_fifo_selected`, `data_out[7:0]` | none |
| can_top | RX synchronizer | Two-flop synchronizer of the asynchronous `rx_i`, reset to 1 (recessive). | `always` 766-778 | `rx_sync_tmp`, `rx_sync` | `rx_sync` | `rx_i`, `clk_i`, `rst` | `rx_sync` | none |

Group boundaries follow function: host-side bus handling, read-path selection, and input synchronization. Every own-logic statement of the active configuration is in exactly one group.

## 4. Signal analysis (inter-block signals at levels 0-1)

Types: **level** = value held until changed; **pulse** = asserted for one clock cycle by construction; **event** = combinational condition that is qualified by a pulse. Evidence in the last column.

### 4.1 Host side

| Signal | Src -> Dst | Width | Type | Meaning | Evidence | Group |
|---|---|---|---|---|---|---|
| cs | Host bus adapter -> i_can_registers, Read-data select | 1 | pulse | Chip select: rising edge of `wr_i` or `rd_i`, qualified by `cs_can_i` | `assign cs = ((wr_i & ~wr_i_q) \| (rd_i & ~rd_i_q)) & cs_can_i` (can_top.v:862); `wr_i_q`, `rd_i_q` are one-cycle delays (847-859) | IF01, IF02 |
| we | Host bus adapter -> i_can_registers, Read-data select | 1 | level | Write indicator = `wr_i` | can_top.v:866 | IF01, IF02 |
| addr[7:0] | Host bus adapter -> i_can_registers, i_can_bsp, Read-data select | 8 | level | Register/FIFO address, latched while `ale_i` is high | can_top.v:837-843, 867 | IF01, IF02, IF03 |
| data_in[7:0] | Host bus adapter -> i_can_registers, i_can_bsp | 8 | level (data) | Write data = `port_0_io` | can_top.v:868 | IF01, IF03 |
| data_out_regs[7:0] | i_can_registers -> Read-data select | 8 | level (data), combinational | Register read data selected by `{extended_mode, addr[4:0]}` | can_registers.v:1093-1141 | IF04 |
| extended_mode, reset_mode | i_can_registers -> Read-data select | 1 each | level | Operating mode selectors, used for FIFO-select decode | can_top.v:746; can_registers.v:536, 808 | IF04 |
| data_out_fifo[7:0] | i_can_bsp -> Read-data select | 8 | level (data) | RX FIFO read data (output of `can_fifo`, `.data_out(data_out)` at can_bsp.v:1404) | can_top.v:621, can_bsp.v:1404 | IF05 |
| data_out_fifo_selected | Read-data select -> i_can_bsp | 1 | level, combinational | 1 when the address maps to the RX buffer window (16..28 extended, 20..29 basic) | can_top.v:744-750 | IF06 |
| data_out[7:0] | Read-data select -> Host bus adapter | 8 | level (data), registered | Byte registered on a read (`cs & ~we`); held until the next read | can_top.v:753-762; driven to `port_0_io` at 869 | IF07 |

### 4.2 can_registers <-> can_bsp

| Signal | Src -> Dst | Width | Type | Meaning | Evidence | Group |
|---|---|---|---|---|---|---|
| reset_mode, listen_only_mode, acceptance_filter_mode, self_test_mode, extended_mode | i_can_registers -> i_can_bsp | 1 each | level | Mode bits from mode/clock-divider registers | can_registers.v:536-539, 808 | Control |
| release_buffer | i_can_registers -> i_can_bsp | 1 | pulse | Release RX buffer command | `assign release_buffer = command[2]` (599); `COMMAND_REG` self-clears with `rst_sync = \|command[3:2] \| reset_mode` (568-575) | Control |
| tx_request | i_can_registers -> i_can_bsp | 1 | level (auto-clearing) | Transmit request; held until the next `sample_point` | `= command[0] \| command[4]` (600); clear at `command[0] & sample_point` (556, 583) | Control |
| abort_tx | i_can_registers -> i_can_bsp | 1 | level (auto-clearing) | Abort request | `= command[1] & ~tx_request` (601); clear at 565 | Control |
| self_rx_request, single_shot_transmission | i_can_registers -> i_can_bsp | 1 each | level | Self-reception / single-shot mode, set by command bits, cleared when `tx_state` falls | can_registers.v:587-612 | Control |
| overload_request | i_can_registers -> i_can_bsp | 1 | constant 0 | Overload requests unsupported | can_registers.v:635 | Control |
| error_warning_limit[7:0] | i_can_registers -> i_can_bsp | 8 | level (data) | Error warning threshold (reset value 96) | can_registers.v:763 | Control |
| we_rx_err_cnt, we_tx_err_cnt | i_can_registers -> i_can_bsp | 1 each | pulse | Host write strobes to the error counters; derive from `cs` (pulse) | can_registers.v:478-479 | Control |
| read_arbitration_lost_capture_reg, read_error_code_capture_reg | i_can_registers -> i_can_bsp | 1 each | pulse | Host read strobes of the capture registers | can_registers.v:453-454 (`read = cs & ~we`) | Control |
| acceptance_code_0..3, acceptance_mask_0..3 | i_can_registers -> i_can_bsp | 8 each | level (data) | Acceptance filter configuration | can_registers.v:863-1074 | Config data |
| tx_data_0..12 | i_can_registers -> i_can_bsp | 8 each | level (data) | Transmit buffer bytes | can_registers.v:884-1004 | Config data |
| node_bus_off, node_error_passive, node_error_active, error_status | i_can_bsp -> i_can_registers | 1 each | level | Fault-confinement state and warning flag | can_bsp.v:2013-2027, 2021, 2086 | Status |
| rx_err_cnt[7:0], tx_err_cnt[7:0] | i_can_bsp -> i_can_registers | 8 each | level (data) | Error counters (bit 8 dropped at can_top.v:670-671) | can_bsp.v:2086; can_top.v:670-671 | Status |
| transmit_status, receive_status, transmitting, need_to_tx | i_can_bsp -> i_can_registers | 1 each | level | Bus-activity and pending-transmit flags | can_bsp.v:2089-2090, 1834-1838 | Status |
| overrun, info_empty, rx_message_counter[6:0] | i_can_bsp -> i_can_registers | 1, 1, 7 | level (data) | RX FIFO overrun, empty flag, message count (registers detect the `overrun` edge with `overrun_q`) | can_bsp.v:1405-1407; can_registers.v:685 | Status |
| error_capture_code[7:0], arbitration_lost_capture[4:0] | i_can_bsp -> i_can_registers | 8, 5 | level (data) | Capture register content | can_bsp.v:2106-2111; can_registers.v:1101-1102 | Status |
| tx_state, tx_state_q, overload_frame | i_can_bsp -> i_can_registers | 1 each | level | Transmit state feedback | can_bsp.v:1796-1811; can_registers.v:593, 610 | Status |
| set_reset_mode | i_can_bsp -> i_can_registers | 1 | pulse | Entering bus-off forces reset mode | `= node_bus_off & ~node_bus_off_q` (can_bsp.v:2085) | Event |
| set_bus_error_irq | i_can_bsp -> i_can_registers | 1 | event (pulse-qualified) | Bus-error interrupt request | `= go_error_frame & ~error_capture_code_blocked` (2127) | Event |
| set_arbitration_lost_irq | i_can_bsp -> i_can_registers | 1 | pulse | Arbitration-lost interrupt request | `= arbitration_lost & ~arbitration_lost_q & ~arbitration_blocked` (1915) | Event |
| tx_successful | i_can_bsp -> i_can_registers | 1 | event | Successful transmission completed; consumer detects its rising edge | `can_bsp.v:1762`; `can_registers.v:663` | Event |

### 4.3 can_btl, can_bsp, can_registers, synchronizer

| Signal | Src -> Dst | Width | Type | Meaning | Evidence | Group |
|---|---|---|---|---|---|---|
| sample_point | i_can_btl -> i_can_bsp, i_can_registers | 1 | pulse | Bit sample instant | Set in a `clk_en_q` cycle and cleared in the next cycle because `clk_en_q` cannot repeat at consecutive cycles (`preset_cnt >= 2`): can_btl.v:257, 275-293, 403-430 | Bit sampling, Sample-point event |
| tx_point | i_can_btl -> i_can_bsp | 1 | pulse | Bit transmit instant | `tx_point <= ~tx_point & ...` guarantees a single cycle (can_btl.v:304-312) | Bit sampling |
| sampled_bit, sampled_bit_q | i_can_btl -> i_can_bsp | 1 each | level (registered) | Sampled bus value (optionally majority of 3) and its previous value | can_btl.v:403-430 | Bit sampling |
| hard_sync | i_can_btl -> i_can_bsp | 1 | level (combinational) | Hard synchronization condition on the dominant edge | can_btl.v:258 | Bit sampling |
| baud_r_presc[5:0], sync_jump_width[1:0], time_segment1[3:0], time_segment2[2:0], triple_sampling | i_can_registers -> i_can_btl | 6, 2, 4, 3, 1 | level (static data) | Bit timing configuration; writable only in reset mode | can_registers.v:446-447, 742-743, 756-758 | Bit timing config |
| rx_idle, rx_inter, transmitting, transmitter | i_can_bsp -> i_can_btl | 1 each | level | Receiver/transmitter state flags | can_bsp.v:757-761, 938-942, 1820-1838 | Bit stream control |
| go_rx_inter, go_overload_frame, go_error_frame, go_tx | i_can_bsp -> i_can_btl | 1 each | event (combinational, qualified by `sample_point`/error terms) | State-transition requests | can_bsp.v:715, 717, 721, 1778 | Bit stream control |
| send_ack | i_can_bsp -> i_can_btl | 1 | level (combinational) | Acknowledge slot drive | can_bsp.v:1598 | Bit stream control |
| tx_next | i_can_bsp -> i_can_btl | 1 | level (combinational) | Next transmit bit value | can_bsp.v:1606-1634 | Bit stream control |
| node_error_passive | i_can_bsp -> i_can_btl | 1 | level | Error-passive state | can_bsp.v:2013-2017 | Bit stream control |
| tx (= tx_o) | i_can_bsp -> i_can_btl | 1 | level (registered) | Transmit line fed back to the bit timing logic | can_bsp.v:1640-1646; can_top.v:567-568, 722 | Bit stream control |
| rx_sync | RX synchronizer -> i_can_btl | 1 | level (registered) | Synchronized receive line | can_top.v:766-778, 567 | RX synchronized |

### 4.4 External ports of can_top (active configuration)

| Port | Dir | Width | Type | Meaning | Evidence | Group |
|---|---|---|---|---|---|---|
| ale_i, rd_i, wr_i, cs_can_i | in | 1 each | level | Host strobes (active high; revision note: negate externally for 8051) | can_top.v:277-282, 119-121 | Host bus control |
| port_0_io[7:0] | inout | 8 | level (data) | Multiplexed address/data. Address captured on `ale_i`; write data read here; read data driven when `cs_can_i & rd_i` | can_top.v:281, 842, 868-869 | Host data bus |
| rx_i | in | 1 | level | CAN bus receive line | can_top.v:290, 775 | CAN RX |
| tx_o | out | 1 | level (registered, reset 1) | CAN bus transmit line | can_bsp.v:1640-1646 | CAN TX |
| bus_off_on | out | 1 | level | `~node_bus_off`: low while the node is bus-off | can_bsp.v:2083 | Bus-off status |
| irq_on | out | 1 | level (latched, active low) | Interrupt request, set low when any enabled interrupt is pending, cleared on IRQ register read or `release_buffer` | can_registers.v:1243-1251 | Interrupt |
| clkout_o | out | 1 | clock | Programmable clock output: constant 1, `clk`, or divided clock | can_registers.v:851 | Clock output |
| clk_i | in | 1 | clock | Core clock | can_top.v:289 | Clock/reset |
| rst_i | in | 1 | level (asynchronous, active high) | Reset (`posedge rst` in all sequential blocks) | can_top.v:277, 865, 766 | Clock/reset |

## 5. Interface classification

No standard bus protocol (APB, AXI, Wishbone, AHB) is active in this configuration. The WISHBONE alternative exists only in the inactive branch.

| Interface | Category | Protocol | Active side -> passive side (evidence) | Mandatory signals / missing | Evidence |
|---|---|---|---|---|---|
| HOST (host bus control and bidirectional data) | custom, protocol-like (8051 multiplexed address/data) | none verified | Host -> TOP: host drives `ale_i`, `rd_i`, `wr_i`; data port is bidirectional | The code documents no protocol; timing not checked | can_top.v:277-287, 836-869 |
| Host register access, Host access qualifier, FIFO access | custom | none | Host bus adapter -> consumer (drives address, write strobe, data) | - | can_top.v:862-868 |
| Register read, FIFO read data, Read data return | custom (data return) | none | Producer drives data: i_can_registers / i_can_bsp -> Read-data select -> Host bus adapter | - | can_registers.v:1093; can_top.v:753-762 |
| FIFO select | custom | none | Read-data select -> i_can_bsp (decode drives select) | - | can_top.v:744-750 |
| Control | custom | none | i_can_registers -> i_can_bsp (host-written control drives the bit stream processor) | - | section 4.2 |
| Config data | custom | none | i_can_registers -> i_can_bsp | - | section 4.2 |
| Status, Event | custom | none | i_can_bsp -> i_can_registers (producer reports) | - | section 4.2 |
| Bit timing config | custom | none | i_can_registers -> i_can_btl | - | section 4.3 |
| Bit sampling, Sample-point event | custom (event/data) | none | i_can_btl -> consumers (timing source) | - | can_btl.v |
| Bit stream control | custom | none | i_can_bsp -> i_can_btl | - | can_bsp.v, can_btl.v |
| RX synchronized | custom | none | RX synchronizer -> i_can_btl | - | can_top.v:766-778 |
| CAN RX / CAN TX | custom (CAN bus lines) | CAN physical layer is outside the RTL (external transceiver) | External -> RX synchronizer; i_can_bsp -> external | - | can_top.v:290-291 |
| Interrupt | custom (level, active low) | none | i_can_registers -> external | - | can_registers.v:1243 |
| Bus-off status, Clock output | custom | none | i_can_bsp / i_can_registers -> external | - | can_bsp.v:2083; can_registers.v:851 |
| Clock/reset | custom | none | External -> all blocks | - | can_top.v:289 |

No catalog-external signal group was found, so no `(proposed group)` exists.

## 6. Interfaces and signal groups (mnemonics, RHD-059, RHD-074)

Signals that belong together functionally form ONE interface, drawn as one connector whose arrow points from the initiating side (request/response pairs and bus-like sets are not split by direction). The complete signal lists per direction are in the Interface Table of the diagram and repeated here.

| Mnemonic | Interface | Endpoints (initiator first) | Signals (all, by direction) |
|---|---|---|---|
| HOST | Host bus (8051-style) | external host -> Host bus adapter | ale_i, rd_i, wr_i, cs_can_i; port_0_io[7:0] (bidirectional) |
| HRA | Host register access | Host bus adapter -> i_can_registers | cs [pulse], we, addr[7:0], data_in[7:0] |
| HRS | Host read select | Host bus adapter -> Read-data select | request: cs [pulse], we, addr[7:0]; return: data_out[7:0] |
| FAC | FIFO access | Host bus adapter -> i_can_bsp | addr[7:0], data_in[7:0] |
| RRD | Register read data | i_can_registers -> Read-data select | data_out_regs[7:0], extended_mode, reset_mode |
| FRI | FIFO read | Read-data select -> i_can_bsp | request: data_out_fifo_selected; return: data_out_fifo[7:0] |
| CSI | Control and status | i_can_registers -> i_can_bsp | registers -> bsp: reset_mode, listen_only_mode, acceptance_filter_mode, self_test_mode, extended_mode, release_buffer, tx_request, abort_tx, self_rx_request, single_shot_transmission, overload_request, error_warning_limit[7:0], we_rx_err_cnt, we_tx_err_cnt, read_arbitration_lost_capture_reg, read_error_code_capture_reg, acceptance_code_0..3[7:0], acceptance_mask_0..3[7:0], tx_data_0..12[7:0], clear_data_overrun (open); bsp -> registers: node_bus_off, node_error_passive, node_error_active, error_status, rx_err_cnt[7:0], tx_err_cnt[7:0], transmit_status, receive_status, transmitting, tx_successful, need_to_tx, overrun, info_empty, rx_message_counter[6:0], error_capture_code[7:0], arbitration_lost_capture[4:0], tx_state, tx_state_q, overload_frame, set_reset_mode, set_bus_error_irq, set_arbitration_lost_irq |
| BTI | Bit timing | i_can_registers -> i_can_btl | registers -> btl: baud_r_presc[5:0], sync_jump_width[1:0], time_segment1[3:0], time_segment2[2:0], triple_sampling; btl -> registers: sample_point |
| BSI | Bit stream | i_can_btl -> i_can_bsp | btl -> bsp: sample_point, tx_point, sampled_bit, sampled_bit_q, hard_sync; bsp -> btl: rx_idle, rx_inter, transmitting, transmitter, go_rx_inter, go_overload_frame, go_error_frame, go_tx, send_ack, tx_next, node_error_passive, tx |
| rx_sync | RX synchronized | RX synchronizer -> i_can_btl | rx_sync |
| rx_i | CAN RX (dedicated pad line) | external -> RX synchronizer | rx_i |
| tx_o | CAN TX (dedicated pad line) | i_can_bsp -> external | tx_o |
| bus_off_on | Bus-off status | i_can_bsp -> external | bus_off_on |
| irq_on | Interrupt | i_can_registers -> external | irq_on |
| clkout_o | Clock output | i_can_registers -> external | clkout_o |
| CLK | Clock/reset | external -> all six blocks (one entry point, distribution tree with one branch per block) | clk_i; rst_i (not used by Read-data select) |

The initiator of CSI is the register file (it carries host-written control and configuration; the status information returns), of BTI the register file (it supplies the timing configuration), and of BSI the bit-timing logic (it supplies the sample and transmit instants that sequence the frame-processing engine). *Interpretation:* these initiator choices follow the direction of control, not a protocol label in the RTL.

`Ungrouped`: none. `rst_i` reaches the children as `rst` through the rename `assign rst = rst_i` (can_top.v:865). The signal group names used in section 4 (Control, Config data, Status, Event, and the separate host-bus signal rows) map to CSI and HOST.

## 7. Conditional and unresolved items

- Active hierarchy is configuration dependent: with `CAN_WISHBONE_IF` defined, the host adapter changes to a WISHBONE synchronizer (can_top.v:782-831) and the functional groups would differ. Not drawn.
- `CAN_BIST` and vendor RAM macros are inactive; `can_fifo` selects its RAM implementation by macro (can_fifo.v:382-512). Level-2 content is outside the selected level.
- `can_top.v:589, 666`: `rx_inter` is connected to both children but has no declaration in `can_top`; it is an implicit 1-bit wire. `not_first_bit_of_inter` (can_top.v:407) is driven by `i_can_bsp` and not used elsewhere. `clear_data_overrun` of `i_can_registers` is left open (can_top.v:482).
- `overload_request` is constant 0 (`can_registers.v:635`) and `overload_frame` feedback is connected but its consumer is commented out.
- Level-1 modules at level N are not expanded: can_registers, can_btl, can_bsp each have own logic that was not grouped (RHD-084).
- All signal types in section 4 come from static reading; none are verified by simulation.

## 8. Diagram mapping

| Page | Blocks | Connectors |
|---|---|---|
| 01_LEVEL_1 | Frame TOP (can_top) enclosing i_can_registers, i_can_btl, i_can_bsp, Host bus adapter, Read-data select, RX synchronizer | No hierarchy arrows (hierarchy is shown by the enclosing frame); 9 internal interface connectors (HRA, HRS, FAC, RRD, FRI, CSI, BTI, BSI, rx_sync), 7 external interfaces (HOST, rx_i, tx_o, bus_off_on, irq_on, clkout_o, CLK with one clock/reset distribution tree); the Interface Table below the diagram lists every signal |
