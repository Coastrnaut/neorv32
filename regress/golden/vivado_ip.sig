version 1
test vivado_default
tb tb_vivado_ip
args 
image c60ccfadb4caf35a
cycles 40010
window 128 2048
stdout 20eeeccf4a5e6fbc 7
global 0:7d7bff
signal ocd_resetn 2 09da54e93832ccd3 0:146d3e
signal wdt_resetn 2 09da54e93832ccd3 0:146d3e
signal m_axi_awaddr 1 2c7957ee48c0632f 0:745980
signal m_axi_awlen 1 06a2fe42ef10160e 0:911e41
signal m_axi_awsize 1 e30b89148a940c0d 0:ec08f3
signal m_axi_awburst 1 38b38fd8f4b528bc 0:381ad6
signal m_axi_awcache 1 f9998dc225f819cb 0:2008a6
signal m_axi_awprot 1 e30b89148a940c0d 0:ec08f3
signal m_axi_awvalid 1 76eb67cc985978ad 0:3b2152
signal m_axi_wdata 1 2c7957ee48c0632f 0:745980
signal m_axi_wstrb 1 f9998dc225f819cb 0:2008a6
signal m_axi_wlast 1 76eb67cc985978ad 0:3b2152
signal m_axi_wvalid 1 76eb67cc985978ad 0:3b2152
signal m_axi_araddr 1 2c7957ee48c0632f 0:745980
signal m_axi_arlen 1 06a2fe42ef10160e 0:911e41
signal m_axi_arsize 1 e30b89148a940c0d 0:ec08f3
signal m_axi_arburst 1 38b38fd8f4b528bc 0:381ad6
signal m_axi_arcache 1 f9998dc225f819cb 0:2008a6
signal m_axi_arprot 1 e30b89148a940c0d 0:ec08f3
signal m_axi_arvalid 1 76eb67cc985978ad 0:3b2152
signal m_axi_rready 1 76eb67cc985978ad 0:3b2152
signal m_axi_bready 1 76eb67cc985978ad 0:3b2152
signal s0_axis_tvalid 1 59b70cfcb99bce28 0:b1beb0
signal s0_axis_tdata 1 54dc54f3e6c0dad3 0:a7b22a
signal s0_axis_tlast 1 59b70cfcb99bce28 0:b1beb0
signal s1_axis_tready 1 59b70cfcb99bce28 0:b1beb0
signal dmi_rsp_data_o 1 54dc54f3e6c0dad3 0:a7b22a
signal dmi_rsp_ack_o 1 59b70cfcb99bce28 0:b1beb0
signal jtag_tdo_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_ioen_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_sck_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_csn_o 1 95029b21ce8a9548 0:9ced73
signal smc_sdo_o 1 59b70cfcb99bce28 0:b1beb0
signal gpio_dir_o 1 59b70cfcb99bce28 0:b1beb0
signal gpio_o 1 59b70cfcb99bce28 0:b1beb0
signal uart0_txd_o 1 59b70cfcb99bce28 0:b1beb0
signal uart0_rtsn_o 1 b171e99a0ef8f300 0:aa8ff1
signal uart1_txd_o 1 59b70cfcb99bce28 0:b1beb0
signal uart1_rtsn_o 1 b171e99a0ef8f300 0:aa8ff1
signal spi_clk_o 1 59b70cfcb99bce28 0:b1beb0
signal spi_dat_o 1 59b70cfcb99bce28 0:b1beb0
signal spi_csn_o 1 b0a6c332075f5373 0:d0104a
signal sdi_dat_o 1 59b70cfcb99bce28 0:b1beb0
signal twi_sda_o 1 b171e99a0ef8f300 0:aa8ff1
signal twi_scl_o 1 b171e99a0ef8f300 0:aa8ff1
signal twd_sda_o 1 b171e99a0ef8f300 0:aa8ff1
signal onewire_o 1 b171e99a0ef8f300 0:aa8ff1
signal pwm_o 1 59b70cfcb99bce28 0:b1beb0
signal cfs_out_o 1 38589260f0f9e2f6 0:8beb7e
signal neoled_o 1 59b70cfcb99bce28 0:b1beb0
signal mtime_time_o 1 9a77a4f5ef240bd1 0:cd6e45

version 1
test vivado_full
tb tb_vivado_ip
args -gBOOT_MODE_SELECT=2 -gDMEM_EN=true -gIMEM_EN=true -gIO_SLINK_EN=true -gOCD_EN=true -gRISCV_ISA_C=true -gXBUS_EN=true
image c60ccfadb4caf35a
cycles 40010
window 128 2048
stdout 7d33d4ccbdcaad83 7
global 0:55dba4
signal ocd_resetn 2 09da54e93832ccd3 0:146d3e
signal wdt_resetn 2 09da54e93832ccd3 0:146d3e
signal m_axi_awaddr 1 54dc54f3e6c0dad3 0:a7b22a
signal m_axi_awlen 1 a7e439a3a29cc3bc 0:c9dad8
signal m_axi_awsize 1 5fef3516c9a73393 0:87dc32
signal m_axi_awburst 1 b171e99a0ef8f300 0:aa8ff1
signal m_axi_awcache 1 95029b21ce8a9548 0:9ced73
signal m_axi_awprot 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_awvalid 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_wdata 1 2c7957ee48c0632f 0:745980
signal m_axi_wstrb 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_wlast 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_wvalid 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_araddr 1 54dc54f3e6c0dad3 0:a7b22a
signal m_axi_arlen 1 a7e439a3a29cc3bc 0:c9dad8
signal m_axi_arsize 1 5fef3516c9a73393 0:87dc32
signal m_axi_arburst 1 b171e99a0ef8f300 0:aa8ff1
signal m_axi_arcache 1 95029b21ce8a9548 0:9ced73
signal m_axi_arprot 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_arvalid 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_rready 1 59b70cfcb99bce28 0:b1beb0
signal m_axi_bready 1 59b70cfcb99bce28 0:b1beb0
signal s0_axis_tvalid 1 59b70cfcb99bce28 0:b1beb0
signal s0_axis_tdata 1 2c7957ee48c0632f 0:745980
signal s0_axis_tlast 1 76eb67cc985978ad 0:3b2152
signal s1_axis_tready 1 59b70cfcb99bce28 0:b1beb0
signal dmi_rsp_data_o 1 54dc54f3e6c0dad3 0:a7b22a
signal dmi_rsp_ack_o 1 59b70cfcb99bce28 0:b1beb0
signal jtag_tdo_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_ioen_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_sck_o 1 59b70cfcb99bce28 0:b1beb0
signal smc_csn_o 1 95029b21ce8a9548 0:9ced73
signal smc_sdo_o 1 59b70cfcb99bce28 0:b1beb0
signal gpio_dir_o 1 59b70cfcb99bce28 0:b1beb0
signal gpio_o 1 59b70cfcb99bce28 0:b1beb0
signal uart0_txd_o 1 59b70cfcb99bce28 0:b1beb0
signal uart0_rtsn_o 1 b171e99a0ef8f300 0:aa8ff1
signal uart1_txd_o 1 59b70cfcb99bce28 0:b1beb0
signal uart1_rtsn_o 1 b171e99a0ef8f300 0:aa8ff1
signal spi_clk_o 1 59b70cfcb99bce28 0:b1beb0
signal spi_dat_o 1 59b70cfcb99bce28 0:b1beb0
signal spi_csn_o 1 b0a6c332075f5373 0:d0104a
signal sdi_dat_o 1 59b70cfcb99bce28 0:b1beb0
signal twi_sda_o 1 b171e99a0ef8f300 0:aa8ff1
signal twi_scl_o 1 b171e99a0ef8f300 0:aa8ff1
signal twd_sda_o 1 b171e99a0ef8f300 0:aa8ff1
signal onewire_o 1 b171e99a0ef8f300 0:aa8ff1
signal pwm_o 1 59b70cfcb99bce28 0:b1beb0
signal cfs_out_o 1 38589260f0f9e2f6 0:8beb7e
signal neoled_o 1 59b70cfcb99bce28 0:b1beb0
signal mtime_time_o 1 9a77a4f5ef240bd1 0:cd6e45
