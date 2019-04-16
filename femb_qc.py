# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/16/2019 10:32:19 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
import numpy as np
#import scipy as sp
#import pylab as pl

import sys 
import string
import time
from datetime import datetime
import struct
import codecs
from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile


class FEMB_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.userdir = "D:/SBND_QC/"
        self.user_f = self.userdir + "FEMB_QCindex.csv"
        self.databkdir = "D:/SBND_QC/FEMB_QC/"
        self.f_qcindex = self.databkdir + "FEMB_QCindex.csv"
        self.femb_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
        self.CLS = CLS_CONFIG()
        self.CLS.WIB_IPs = self.WIB_IPs
        self.CLS.FEMB_ver = 0x501
        self.CLS.jumbo_flag = self.jumbo_flag 
        self.RAW_C = RAW_CONV()
        self.RAW_C.jumbo_flag = self.jumbo_flag 
        self.raw_data = []

    def FEMB_INDEX_LOAD(self):
        self.femb_qclist = []
        with open(self.f_qcindex, 'r') as fp:
            for cl in fp:
                tmp = cl.split(',')
                x = []
                for i in tmp:
                    x.append(i.replace(" ", ""))
                x = x[:-1]
                if (x[0][0] != "#"):
                    self.femb_qclist.append(x[1:])
        femb_ids = []
        for femb in self.femb_qclist:
            femb_ids.append(fm[1])
        return femb_ids

    def FEMB_QC_Input(self):
        FEMBlist = self.FEMB_INDEX_LOAD()
        FEMB_infos = []
        env = input("Test is performed at (RT or LN)? :")
        for i in range(4):
            while (True):
                print ("Please enter ID of FEMB in WIB slot%d (input \"OFF\" if no FEMB): "%i)
                FEMB_id = input("Format: FM-AM (e.g. FC1-SAC1) >>")
                cf = input("WIB slot%d with FEMB ID is \"#%s\", Y or N? "%(i, FEMB_id) )
                if (cf == "Y"):
                    break
            if FEMB_id in FEMBlist:
                print ("FEMB \"%s\" has been tested before, please input a short note for this retest\n"%FEMB_id)
                c_ret = input("Reason for retest: ")
                rerun_f = "Y"
            else:
                c_ret = ""
                rerun_f = "N"
            FEMB_infos.append("SLOT%d"%i + "\n" + FEMB_id + "\n" + env + "\n" + rerun_f + "\n" + c_ret )
        return FEMB_infos

    def FEMB_CHK_ACQ(self, testcode = 0):
        self.CLS.val = 100 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()
        if testcode == 1:
            #14mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        elif testcode == 2:
            #7.8mV/fC, 2.0us, 900mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, swdac1=1, swdac2=0, data_cs=0)
        elif testcode == 3:
            #7.8mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        elif testcode == 4:
            #14mV/fC, 2.0us, 200mV, ASIC_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=0, swdac2=1, dac= 0x08, data_cs=0)
        else:
            #14mV/fC, 2.0us, 900mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=1, swdac2=0, data_cs=0)

        qc_data = self.CLS.TPC_UDPACQ(cfglog)
        self.CLS.FEMBs_CE_OFF()
        return qc_data

    def FEMB_BL_RB(self,  snc=1, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1): #default 14mV/fC, 2.0us, 200mV
        self.CLS.val = 10 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()

        w_f_bs = []
        self.CLS.FEREG_MAP.set_fe_board(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, smn=0, sdf=sdf, slk0=slk0, slk1=slk1 )
        self.CLS.fecfg_loadflg = True
        self.CLS.fe_monflg = True

        for chn in range(128):
            print ("Baseline of CHN%d of all available FEMBs are being measured by the monitoring ADC"%chn)
            chipn = int(chn//16)
            chipnchn = int(chn%16)

            self.CLS.FEREG_MAP.set_fechn_reg(chip=chipn, chn=chipnchn, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, smn=1, sdf=sdf )
            self.CLS.REGS = self.CLS.FEREG_MAP.REGS
            cfglog = self.CLS.CE_CHK_CFG(mon_cs = 1)
            for acfg in cfglog:
                w_f_b_new = True
                for i in range(len(w_f_bs)):
                    if w_f_bs[i][0] == acfg[0] and w_f_bs[i][1] == acfg[1] :
                        w_f_bs[i][2].append(acfg[30])
                        w_f_bs[i][3].append(acfg[31])
                        w_f_b_new = False
                        break
                if w_f_b_new :
                    w_f_bs.append([acfg[0], acfg[1], [acfg[30]], [acfg[31]]])

        self.CLS.fecfg_loadflg = False
        self.CLS.fe_monflg = False
        self.CLS.CE_CHK_CFG(mon_cs = 0) #disable monitoring and return to default setting
        return w_f_bs

    def FEMB_Temp_RB(self ):
        self.CLS.val = 10 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()

        w_f_bs = []
        self.CLS.FEREG_MAP.set_fe_board(smn=0 )
        self.CLS.fecfg_loadflg = True
        self.CLS.fe_monflg = True

        for chip in range(8):
            print ("FE ASIC%d of all available FEMBs are being measured by the monitoring ADC"%chip)
            chipn = chip
            chipnchn = 0

            self.CLS.FEREG_MAP.set_fechip_global(chip=chipn, stb=1, stb1=0 )
            self.CLS.FEREG_MAP.set_fechn_reg(chip=chipn, chn=chipnchn,  smn=1 )
            self.CLS.REGS = self.CLS.FEREG_MAP.REGS
            cfglog = self.CLS.CE_CHK_CFG(mon_cs = 1)
            for acfg in cfglog:
                w_f_b_new = True
                for i in range(len(w_f_bs)):
                    if w_f_bs[i][0] == acfg[0] and w_f_bs[i][1] == acfg[1] :
                        w_f_bs[i][2].append(acfg[30])
                        w_f_bs[i][3].append(acfg[31])
                        w_f_b_new = False
                        break
                if w_f_b_new :
                    w_f_bs.append([acfg[0], acfg[1], [acfg[30]], [acfg[31]]])

        print (w_f_bs)
        self.CLS.fecfg_loadflg = False
        self.CLS.fe_monflg = False
        self.CLS.CE_CHK_CFG(mon_cs = 0) #disable monitoring and return to default setting
        return w_f_bs
           
    def FEMB_CHK_ANA(self, FEMB_infos, qc_data, pwr_i = 1):
        qcs = []
        for femb_info in FEMB_infos:
            fembs = femb_info.split("\n")
            femb_addr = int(fembs[0][4])
            femb_id = fembs[1]
            femb_env = fembs[2]
            femb_rerun_f = fembs[3]
            femb_c_ret = fembs[4]
            femb_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") +5: self.CLS.err_code.index("#IP")] 
            errs = self.CLS.err_code.split("SLOT")
            for er in errs[1:]:
                if( int(er[0]) == femb_addr ):
                    if (len(er) <2 ):
                        femb_errlog = ""
                    else:
                        femb_errlog = er[2: er.index("#IP")] if "#IP" in er else er[2: ]
                    break

            if  "OFF" in femb_id:
                pass
            else :
                qc_list = ["FAIL", femb_env, femb_id, femb_rerun_f, femb_date, femb_errlog, femb_c_ret, "PWR%d"%pwr_i] 
                map_r = None
                sts = None
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr): 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fembdata = fdata[1]
                        map_r = self.FEMB_CHK( femb_addr, fembdata)
                        sts = fdata[2]
                        if (len(femb_errlog) == 0):
                            if map_r[0] : 
                                qc_list[0] = "PASS" 
                            else:
                                qc_list[0] = "FAIL" 
                                qc_list[-3] += map_r[1]
                        break
                qcs.append(qc_list )
                self.raw_data.append([qc_list, map_r, sts, fdata[0]])
        return qcs

    def FEMB_CHK(self,  femb_addr, fembdata):
        chn_rmss = []
        chn_peds = []
        chn_pkps = []
        chn_pkns = []
        chn_waves = []
        for adata in fembdata:
            chn_data, feed_loc, chn_peakp, chn_peakn = self.RAW_C.raw_conv_peak(adata)
            for achn in range(len(chn_data)):
                achn_ped = []
                for af in range(len(feed_loc[0:-2])):
                    achn_ped += chn_data[achn][feed_loc[af]+100: feed_loc[af+1] ] 
                arms = np.std(achn_ped)
                aped = int(np.mean(achn_ped))
                apeakp = int(np.mean(chn_peakp[achn]))
                apeakn = int(np.mean(chn_peakn[achn]))
                chn_rmss.append(arms)
                chn_peds.append(aped)
                chn_pkps.append(abs(apeakp-aped))
                chn_pkns.append(abs(apeakn-aped))
                chn_waves.append( chn_data[achn][feed_loc[0]: feed_loc[1]] )
        ana_err_code = ""
        rms_mean = np.mean(chn_rmss)
        rms_thr = 5*np.std(chn_rmss) if 5*(np.std(chn_rmss) < 0.5*rms_mean) else 0.5*rms_mean
        for chn in range(128):
            if abs(chn_rmss[chn] - rms_mean) < rms_thr :
                pass
            else:
                ana_err_code += "-F9_RMS_CHN%d"%(chn)

        for gi in range(4): 
            ped_mean = np.mean(chn_peds[gi*32 : (gi+1)*32])
            pkp_mean = np.mean(chn_pkps[gi*32 : (gi+1)*32])
            pkn_mean = np.mean(chn_pkns[gi*32 : (gi+1)*32])
            ped_thr= 30 
            for chn in range(gi*32, (gi+1)*32, 1):
                if chn_pkps[chn] < 200:
                    ana_err_code += "-F9_NORESP_CHN%d"%(chn)
                if chn_pkns[chn] < 200:
                    ana_err_code += "-F9_NORESN_CHN%d"%(chn)
                if abs(chn_peds[chn] - ped_mean) > ped_thr :
                    ana_err_code += "-F9_PED_CHN%d"%(chn)
                if abs(1- chn_pkps[chn]/pkp_mean) > 0.2:
                    ana_err_code += "-F9_PEAKP_CHN%d"%(chn)
                if abs(1- chn_pkns[chn]/pkn_mean) > 0.2:
                    ana_err_code += "-F9_PEAKN_CHN%d"%(chn)
        if len(ana_err_code) > 0:
            return (False, ana_err_code, [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves])
        else:
            return (True, "-PASS", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves])

    def FEMB_QC_PWR(self, FEMB_infos):
        pwr_qcs = []
        for pwr_i in range(1, self.pwr_n+1 ):
            print ("Power Cycle %d of %d starts..."%(pwr_i, self.pwr_n))
            qc_data = self.FEMB_CHK_ACQ(testcode = pwr_i)
            qcs = self.FEMB_CHK_ANA(FEMB_infos, qc_data, pwr_i)
            pwr_qcs += qcs
            print ("Power Cycle %d of %d is done, wait 30 seconds"%(pwr_i, self.pwr_n))
            time.sleep(30)

        saves = []
        for femb_info in FEMB_infos:
            fembs = femb_info.split("\n")
            femb_id = fembs[1]
            flg = False
            for qct in pwr_qcs:
                if qct[2] == femb_id :
                    if qct[0] == "PASS" :
                        pass_qct = qct
                        flg = True
                    else:
                        flg = False
                        saves.append(qct)
                        break
            if (flg):
                saves.append(pass_qct)

        with open (self.f_qcindex , 'a') as fp:
            print ("Result,ENV,FM_ID,Retun Test,Date,Error_Code,Note,Powr Cycle,")
            for x in saves:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)
        copyfile(self.f_qcindex, self.user_f )

        if (len(pwr_qcs) > 0 ):
            fn =self.databkdir  + "FEMB_QC_" + pwr_qcs[0][1] +"_" + pwr_qcs[0][4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)
        print ("Result is saved in %s"%self.user_f )
        print ("Well Done")


    def FEMB_SUB_PLOT(self, ax, x, y, title, xlabel, ylabel, color='b', marker='.'):
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        ax.plot(x,y, marker=marker, color=color)

    def FEMB_PLOT(self):
        import matplotlib.pyplot as plt
        if len(self.raw_data) != 0: 
            for a_femb_data in self.raw_data:
                qc_list = a_femb_data[0]
                qc_pf = qc_list[0]
                env = qc_list[1]
                femb_id = qc_list[2]
                femb_rerun_f = qc_list[3]
                femb_date = qc_list[4]
                femb_errlog = qc_list[5]
                femb_c_ret = qc_list[6]
                femb_pwr = qc_list[7]
                map_r = a_femb_data[1]
                map_pf = map_r[0]
                map_pf_str = map_r[1]
                chn_rmss = map_r[2][0] # 128chn list, each element is a integal
                chn_peds = map_r[2][1] # 128chn list, each element is a float
                chn_pkps = map_r[2][2] # 128chn list, each element is a integal
                chn_pkns = -(abs(np.array(map_r[2][3]))) # 128chn list, each element is a integal
                chn_wfs  = map_r[2][4] # 128chn list, each element is a list
                d_sts = a_femb_data[2][0]
                d_sts_keys = list(d_sts.keys())
                wib_ip = a_femb_data[3][0]
                femb_addr = a_femb_data[3][1]

                fpgadac_en = a_femb_data[3][6]
                asicdac_en = a_femb_data[3][7]
                fpgadac_v  = a_femb_data[3][8]
                snc  = a_femb_data[3][14]
                sg0  = a_femb_data[3][15]
                sg1  = a_femb_data[3][16]
                st0  = a_femb_data[3][17]
                st1  = a_femb_data[3][18]
                sdf  = a_femb_data[3][20]
                asicdac_v = a_femb_data[3][29]
                if fpgadac_en:
                    cali_str = "FPGA-DAC(%02x)"%fpgadac_v
                elif asicdac_en:
                    cali_str = "ASIC-DAC(%02x)"%asicdac_v
                else:
                    cali_str = "No pulser"%asicdac_v
                snc_str = "FE Baseline 200mV" if snc==1 else "FE Baseline 900mV"
                sdf_str = "FE Buffer ON" if sdf==1 else "FE Buffer OFF"
                if sg0 == 0 and sg1 == 0:
                    sg_str = "4.7mV/fC"
                elif sg0 == 1 and sg1 == 0:
                    sg_str = "7.8mV/fC"
                elif sg0 == 0 and sg1 == 1:
                    sg_str = "14mV/fC"
                else:
                    sg_str = "25mV/fC"

                if st0 == 0 and st1 == 0:
                    st_str = "1.0$\mu$s"
                elif st0 == 1 and st1 == 0:
                    st_str = "0.5$\mu$s"
                elif st0 == 0 and st1 == 1:
                    st_str = "3.0$\mu$s"
                else:
                    st_str = "2.0$\mu$s"
               
                fembsts_keys = []
                for akey in d_sts_keys:
                    if (akey == "FEMB%d"%femb_addr):
                        fembsts_keys.append(akey)
                
                fn = self.databkdir + "/" + env + "_" + femb_id + "_" + femb_date + "_" + femb_pwr + ".png"

                fig = plt.figure(figsize=(8.5,11))
                color = "g" if "PASS" in qc_pf else "r"
                fig.suptitle("Test Result of Power Cycle #%s (%s)"%(femb_pwr[-1], qc_pf), color=color, weight ="bold", fontsize = 12)
                fig.text(0.10, 0.94, "Date&Time: %s"%femb_date   )
                fig.text(0.55, 0.94, "Temperature: %s "%env  )
                fig.text(0.10, 0.92, "FEMB ID: %s "%femb_id      )
                fig.text(0.55, 0.92, "STATUS: %s "%qc_pf, color=color, weight ="bold" )
                fig.text(0.10,0.90, "Rerun comment: %s "%femb_c_ret     )
                fig.text(0.10, 0.88, "WIB IP: %s "%wib_ip      )
                fig.text(0.55, 0.88, "FEMB SLOT: %s "%femb_addr     )
                fig.text(0.10, 0.86, "FE Configuration: " + sg_str + ", " + st_str + ", " + snc_str + ", " + sdf_str + ", " + cali_str  )

                fig.text(0.35, 0.83, "Link Status and Power consumption" ,weight ="bold"    )
                fig.text(0.10, 0.81, "LINK: : " + "{0:4b}".format(d_sts["FEMB%d_LINK"%femb_addr])   )
                fig.text(0.55, 0.81, "EQ: : " + "{0:4b}".format(d_sts["FEMB%d_EQ"%femb_addr])      )
                fig.text(0.10, 0.79, "Checksum error counter of LINK0 to LINK3 : %04X, %04X, %04X, %04X"%\
                                      (d_sts["FEMB%d_CHK_ERR_LINK0"%femb_addr], d_sts["FEMB%d_CHK_ERR_LINK1"%femb_addr] ,
                                       d_sts["FEMB%d_CHK_ERR_LINK2"%femb_addr], d_sts["FEMB%d_CHK_ERR_LINK3"%femb_addr] ) )
                fig.text(0.10, 0.77, "Frame error counter of LINK0 to LINK3 : %04X, %04X, %04X, %04X"% \
                                      (d_sts["FEMB%d_FRAME_ERR_LINK0"%femb_addr], d_sts["FEMB%d_FRAME_ERR_LINK1"%femb_addr] ,
                                       d_sts["FEMB%d_FRAME_ERR_LINK2"%femb_addr], d_sts["FEMB%d_FRAME_ERR_LINK3"%femb_addr] ) )
                fig.text(0.10, 0.75, "FEMB Power Consumption = " + "{0:.4f}".format(d_sts["FEMB%d_PC"%femb_addr]) + "W" )

                fig.text(0.10, 0.73, "BIAS = " + "{0:.4f}".format(d_sts["FEMB%d_BIAS_V"%femb_addr]) + \
                                     "V, AM V33 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV33_V"%femb_addr]) + \
                                     "V, AM V28 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV28_V"%femb_addr]) + "V")

                fig.text(0.10, 0.71, "BIAS = " + "{0:.4f}".format(d_sts["FEMB%d_BIAS_V"%femb_addr]) + \
                                     "A, AM V33 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV33_I"%femb_addr]) + \
                                     "A, AM V30 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV28_I"%femb_addr]) + "A")

                fig.text(0.10, 0.69, "FM V39 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV39_V"%femb_addr]) + \
                                     "V, FM V30 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV30_V"%femb_addr]) + \
                                     "V, FM V18 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV18_V"%femb_addr]) + "V" )

                fig.text(0.10, 0.67, "FM V39 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV39_I"%femb_addr]) + \
                                     "A, FM V30 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV30_I"%femb_addr]) + \
                                     "A, FM V18 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV18_I"%femb_addr]) + "A" )
                
                
                if ("PASS" in qc_pf):
                    ax1 = plt.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)
                    ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)
                    ax3 = plt.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=1)
                    ax4 = plt.subplot2grid((3, 2), (2, 1), colspan=1, rowspan=1)
                    chns = range(len(chn_rmss))
                    self.FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
                    self.FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
                    self.FEMB_SUB_PLOT(ax3, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
                    self.FEMB_SUB_PLOT(ax3, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
                    for chni in chns:
                        ts = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
                        x = (np.arange(ts)) * 0.5
                        y = chn_wfs[chni][0:ts]
                        self.FEMB_SUB_PLOT(ax4, x, y, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
                else:
                    cperl = 80
                    lines = int(len(femb_errlog)//cperl) + 1
                    fig.text(0.05,0.65, "Error log: ")
                    for i in range(lines):
                        fig.text(0.10, 0.63-0.02*i, femb_errlog[i*cperl:(i+1)*cperl])
                
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                plt.savefig(fn)
                plt.close()


a = FEMB_QC()
FEMB_infos = ['SLOT0\nFC1-SAC1\nRT\nN\n', 'SLOT1\nFC2-SAC2\nRT\nN\n', 'SLOT2\nFC3-SAC3\nRT\nN\n', 'SLOT3\nFC4-SAC4\nRT\nN\n']
#FEMB_infos = a.FEMB_QC_Input()
#a.FEMB_QC_PWR( FEMB_infos)
#a.FEMB_PLOT()
#a.FEMB_BL_RB(snc=1, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1) #default 14mV/fC, 2.0us, 200mV
a.FEMB_Temp_RB()
#a.FEMB_BL_RB() #default 14mV/fC, 2.0us, 200mV
#fn =a.databkdir  + "\FM_QC_RT_2019_04_09_18_26_28.bin"
#with open(fn, 'rb') as f:
#     a.raw_data = pickle.load(f)
 



