import random
from enum import Enum

#
# These are the event names and ID numbers used to build ASRe records
#  as found in Ericsson 10/ documents such as CXC1735777/26 version R10A
class  InterestingEvents(Enum):
    INTERNAL_EVENT_ANR_PCI_REPORT_WANTED = 5173
    INTERNAL_EVENT_MEASUREMENT_REPORT_RECEIVED = 5262
    INTERNAL_EVENT_S1_ERROR_INDICATION = 5209
    INTERNAL_EVENT_S1_NAS_NON_DELIVERY_INDICATION = 5208
    INTERNAL_EVENT_UE_CAPABILITY = 5172
    INTERNAL_EVENT_UE_MOBILITY_EVAL = 5193
    INTERNAL_EVENT_X2_ERROR_INDICATION = 5210
    INTERNAL_PER_RADIO_UE_MEASUREMENT = 3075
    INTERNAL_PER_RADIO_UE_MEASUREMENT_TA = 3108
    INTERNAL_PER_UE_RB_TRAFFIC_REP = 3077
    INTERNAL_PER_UE_TRAFFIC_REP = 3076
    INTERNAL_PROC_ANR_CGI_REPORT = 4117
    INTERNAL_PROC_ANR_PCI_CONFLICT_CGI_REPORT = 4139
    INTERNAL_PROC_CSG_CELL_CGI_REPORT = 4138
    INTERNAL_PROC_ERAB_MODIFY = 4122
    INTERNAL_PROC_ERAB_RELEASE = 4114
    INTERNAL_PROC_ERAB_SETUP = 4099
    INTERNAL_PROC_HO_EXEC_S1_IN = 4105
    INTERNAL_PROC_HO_EXEC_S1_OUT = 4104
    INTERNAL_PROC_HO_EXEC_X2_IN = 4113
    INTERNAL_PROC_HO_EXEC_X2_OUT = 4112
    INTERNAL_PROC_HO_PREP_S1_IN = 4103
    INTERNAL_PROC_HO_PREP_S1_OUT = 4102
    INTERNAL_PROC_HO_PREP_X2_IN = 4111
    INTERNAL_PROC_HO_PREP_X2_OUT = 4110
    INTERNAL_PROC_INITIAL_CTXT_SETUP = 4106
    INTERNAL_PROC_NON_PLANNED_PCI_CGI_REPORT = 4134
    INTERNAL_PROC_RRC_CONN_RECONF_NO_MOB = 4120
    INTERNAL_PROC_RRC_CONN_SETUP = 4097
    INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT = 4121
    INTERNAL_PROC_S1_SETUP = 4116
    INTERNAL_PROC_S1_SIG_CONN_SETUP = 4098
    INTERNAL_PROC_UE_CTXT_MODIFY = 4126
    INTERNAL_PROC_UE_CTXT_RELEASE = 4125
    INTERNAL_PROC_X2_RESET = 4123
    INTERNAL_PROC_X2_SETUP = 4118
    RRC_CSFB_PARAMETERS_REQUEST_CDMA2000 = 29
    RRC_CSFB_PARAMETERS_RESPONSE_CDMA2000 = 30
    RRC_MOBILITY_FROM_E_UTRA_COMMAND_EXT = 35
    RRC_UL_HANDOVER_PREPARATION_TRANSFER = 32
    S1_DOWNLINK_NAS_TRANSPORT = 1025
    S1_DOWNLINK_S1_CDMA2000_TUNNELING_EXT = 1091
    S1_HANDOVER_REQUEST = 1034
    S1_INITIAL_CONTEXT_SETUP_REQUEST = 1038
    S1_INITIAL_UE_MESSAGE = 1040
    S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE = 1045
    S1_UPLINK_NAS_TRANSPORT = 1067
    X2_CONTEXT_FETCH_RESPONSE = 2072
    X2_HANDOVER_REQUEST = 2058

    RRC_RRC_CONNECTION_RECONFIGURATION = 8
    RRC_RRC_CONNECTION_RECONFIGURATION_COMPLETE = 13

    """    
    # Procedural events
    INTERNAL_PROC_INITIAL_CTXT_SETUP = 4106
    INTERNAL_PROC_RRC_CONN_SETUP = 4097
    INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT = 4121
    INTERNAL_PROC_S1_SIG_CONN_SETUP = 4098
    INTERNAL_PROC_UE_CTXT_RELEASE = 4125
    INTERNAL_PROC_HO_EXEC_S1_OUT = 4104
    INTERNAL_PROC_HO_EXEC_X2_OUT = 4112
    INTERNAL_PROC_HO_EXEC_X2_IN = 4113
    INTERNAL_PROC_HO_EXEC_S1_IN = 4105
    INTERNAL_PROC_HO_PREP_X2_OUT = 4110
    INTERNAL_PROC_HO_PREP_S1_OUT = 4102
    INTERNAL_PROC_HO_PREP_X2_IN = 4111
    INTERNAL_PROC_HO_PREP_S1_IN = 4103

    # Non-procedural status events    
    INTERNAL_EVENT_UE_MOBILITY_EVAL = 5193

    # External protocol events
    S1_HANDOVER_REQUEST = 1034
    S1_INITIAL_UE_MESSAGE = 1040
    S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE = 1045
    S1_INITIAL_CONTEXT_SETUP_REQUEST = 1038  
    X2_CONTEXT_FETCH_RESPONSE = 2072
    X2_HANDOVER_REQUEST = 2058    
        
    # periodic events
    INTERNAL_PER_RADIO_UE_MEASUREMENT = 3075
    INTERNAL_PER_UE_RB_TRAFFIC_REP = 3077
    INTERNAL_PER_UE_TRAFFIC_REP = 3076
    
    # Other events known to Sanjib
    INTERNAL_EVENT_UE_CAPABILITY = 5172
    
    # on my list but not Sanjib's
    INTERNAL_EVENT_ERAB_DATA_INFO = 5202
    INTERNAL_PROC_ERAB_RELEASE = 4114
    INTERNAL_PROC_ERAB_SETUP = 4099
    S1_ERAB_SETUP_REQUEST = 1054
    S1_HANDOVER_REQUEST_ACKNOWLEDGE = 1035
    S1_INITIAL_CONTEXT_SETUP_REQUEST = 1038
    X2_CONTEXT_FETCH_REQUEST = 2071
    X2_HANDOVER_REQUEST_ACKNOWLEDGE = 2059
    """        
    # These are the same events that some have different names from the 10/ document
    #  
    INTERNAL_PROC_HO_S1_EXEC_IN = 4105
    INTERNAL_PROC_HO_S1_EXEC_OUT = 4104
    INTERNAL_PROC_HO_X2_EXEC_IN = 4113
    INTERNAL_PROC_HO_X2_EXEC_OUT = 4112
    INTERNAL_PROC_HO_S1_PREP_IN = 4103
    INTERNAL_PROC_HO_S1_PREP_OUT = 4102
    INTERNAL_PROC_HO_X2_PREP_IN = 4111
    INTERNAL_PROC_HO_X2_PREP_OUT = 4110
    X2_FETCH_CONTEXT_RESPONSE = 2072
    
    # Jaimin's EBS-L only events
    INTERNAL_PER_PARTITION_REPORT = 3117
    INTERNAL_PER_PROCESSOR_LOAD = 3084
    INTERNAL_EVENT_NEIGHBREL_ADD = 5146
    INTERNAL_EVENT_NEIGHBREL_REMOVE = 5147
    INTERNAL_PROC_SCTP_SHUTDOWN = 4124
    INTERNAL_EVENT_ADV_CELL_SUP_DETECTION = 5228
    INTERNAL_EVENT_ADV_CELL_SUP_RECOVERY_ATTEMPT = 5229
    INTERNAL_EVENT_ADV_CELL_SUP_RECOVERY_RESULT = 5230
    INTERNAL_EVENT_CMAS_REQ = 5223
    INTERNAL_EVENT_CMAS_RESP = 5224
    INTERNAL_EVENT_ETWS_REQ = 5221
    INTERNAL_EVENT_ETWS_RESP = 5222
    INTERNAL_PER_EVENT_CMAS_REPET_COMPL = 3107
    
    #
    INTERNAL_EVENT_ERAB_DATA_INFO = 5202

    @classmethod
    def has_value(cls, value):
        return (any(value == item.value for item in cls))

    @classmethod
    def isCommonEvt(cls, value):
        ''' return true if event is common to ASR and EBS-L '''
        return value in [
            InterestingEvents.INTERNAL_PROC_UE_CTXT_RELEASE.value,
            InterestingEvents.INTERNAL_PROC_RRC_CONN_SETUP.value,
            InterestingEvents.INTERNAL_PROC_INITIAL_CTXT_SETUP.value,
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_OUT.value,
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_OUT.value,
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value,
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_IN.value,
            InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value,
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_OUT.value,
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_OUT.value,
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value,
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_IN.value,
            InterestingEvents.INTERNAL_PROC_ERAB_RELEASE.value,
            InterestingEvents.INTERNAL_PROC_ERAB_SETUP.value,

        ]

    @classmethod
    def isASROnlyEvt(cls, value):
        ''' return true if event ASR only '''
        return value in [
            InterestingEvents.INTERNAL_EVENT_UE_MOBILITY_EVAL.value,
            InterestingEvents.INTERNAL_EVENT_UE_CAPABILITY.value,
            InterestingEvents.INTERNAL_PROC_S1_SIG_CONN_SETUP.value,
            InterestingEvents.S1_HANDOVER_REQUEST.value,  
            InterestingEvents.S1_INITIAL_CONTEXT_SETUP_REQUEST.value,
            InterestingEvents.S1_INITIAL_UE_MESSAGE.value,
            InterestingEvents.S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE.value,
            InterestingEvents.X2_CONTEXT_FETCH_RESPONSE.value,
            InterestingEvents.X2_HANDOVER_REQUEST.value,
            InterestingEvents.INTERNAL_PER_RADIO_UE_MEASUREMENT.value,
            InterestingEvents.INTERNAL_PER_UE_RB_TRAFFIC_REP.value,
            InterestingEvents.INTERNAL_PER_UE_TRAFFIC_REP.value,
            InterestingEvents.INTERNAL_EVENT_ERAB_DATA_INFO.value,
            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION.value,
            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION_COMPLETE.value,  # 13


        ]            
    
    @classmethod
    def isEBSLonlyEvt(cls, value):        
        return value in [
            InterestingEvents.INTERNAL_PROC_RRC_CONN_RECONF_NO_MOB.value,
            InterestingEvents.INTERNAL_PER_RADIO_UE_MEASUREMENT_TA.value,
            InterestingEvents.INTERNAL_EVENT_MEASUREMENT_REPORT_RECEIVED.value,
            InterestingEvents.S1_DOWNLINK_NAS_TRANSPORT.value,
            InterestingEvents.S1_UPLINK_NAS_TRANSPORT.value,
            InterestingEvents.INTERNAL_PER_PARTITION_REPORT.value,
            InterestingEvents.INTERNAL_PROC_CSG_CELL_CGI_REPORT.value,
            InterestingEvents.INTERNAL_PROC_NON_PLANNED_PCI_CGI_REPORT.value,
            InterestingEvents.INTERNAL_PROC_UE_CTXT_MODIFY.value,
            InterestingEvents.INTERNAL_EVENT_ANR_PCI_REPORT_WANTED.value,
            InterestingEvents.INTERNAL_PER_PROCESSOR_LOAD.value,
            #InterestingEvents.INTERNAL_PROC_ERAB_SETUP.value,
            #InterestingEvents.INTERNAL_PROC_ERAB_RELEASE.value,
            InterestingEvents.INTERNAL_PROC_ANR_CGI_REPORT.value,
            InterestingEvents.INTERNAL_EVENT_S1_NAS_NON_DELIVERY_INDICATION.value,
            InterestingEvents.INTERNAL_EVENT_S1_ERROR_INDICATION.value,
            InterestingEvents.INTERNAL_PROC_ANR_PCI_CONFLICT_CGI_REPORT.value,
            InterestingEvents.INTERNAL_EVENT_X2_ERROR_INDICATION.value,
            InterestingEvents.INTERNAL_EVENT_NEIGHBREL_ADD.value,
            InterestingEvents.INTERNAL_EVENT_NEIGHBREL_REMOVE.value,
            InterestingEvents.RRC_MOBILITY_FROM_E_UTRA_COMMAND_EXT.value,
            InterestingEvents.INTERNAL_PROC_SCTP_SHUTDOWN.value,
            InterestingEvents.INTERNAL_PROC_X2_SETUP.value,
            InterestingEvents.INTERNAL_PROC_X2_RESET.value,
            InterestingEvents.INTERNAL_EVENT_ADV_CELL_SUP_DETECTION.value,
            InterestingEvents.INTERNAL_EVENT_ADV_CELL_SUP_RECOVERY_ATTEMPT.value,
            InterestingEvents.INTERNAL_EVENT_ADV_CELL_SUP_RECOVERY_RESULT.value,
            InterestingEvents.INTERNAL_EVENT_CMAS_REQ.value,
            InterestingEvents.INTERNAL_EVENT_CMAS_RESP.value,
            InterestingEvents.INTERNAL_EVENT_ETWS_REQ.value,
            InterestingEvents.INTERNAL_EVENT_ETWS_RESP.value,
            InterestingEvents.INTERNAL_PER_EVENT_CMAS_REPET_COMPL.value,
            InterestingEvents.INTERNAL_PROC_ERAB_MODIFY.value,
            InterestingEvents.INTERNAL_PROC_S1_SETUP.value,
            InterestingEvents.RRC_CSFB_PARAMETERS_REQUEST_CDMA2000.value,
            InterestingEvents.RRC_CSFB_PARAMETERS_RESPONSE_CDMA2000.value,
            InterestingEvents.RRC_UL_HANDOVER_PREPARATION_TRANSFER.value,
            InterestingEvents.S1_DOWNLINK_S1_CDMA2000_TUNNELING_EXT.value,
        ]
    
    @classmethod
    def isASRevt(cls, value):
        # As per email from Sanjib 7/12/2017 with S1_NAS replaced with S1_INITIAL_CONTEXT_SETUP_REQUEST
        return value in [
            # Procedural events
            InterestingEvents.INTERNAL_PROC_INITIAL_CTXT_SETUP.value,  # 4106 i1
            InterestingEvents.INTERNAL_PROC_RRC_CONN_SETUP.value,  # 4097
            InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value,  # 4121
            InterestingEvents.INTERNAL_PROC_S1_SIG_CONN_SETUP.value,  # 4098
            InterestingEvents.INTERNAL_PROC_UE_CTXT_RELEASE.value,  # 4125
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_OUT.value,  # 4104
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_OUT.value,  # 4112
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_IN.value,  # 4113
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_IN.value,  # 4105
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_OUT.value,  # 4110
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_OUT.value,  # 4102
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value,  # 4111
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value,  # 4103
        
            # Non-procedural InterestingEvents.Status events    
            InterestingEvents.INTERNAL_EVENT_UE_MOBILITY_EVAL.value,  # 5193
        
            # External protocol events
            InterestingEvents.S1_HANDOVER_REQUEST.value,  # 1034
            InterestingEvents.S1_INITIAL_UE_MESSAGE.value,  # 1040
            InterestingEvents.S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE.value,  # 1045
            InterestingEvents.S1_INITIAL_CONTEXT_SETUP_REQUEST.value,  # 1038  
            InterestingEvents.X2_CONTEXT_FETCH_RESPONSE.value,  # 2072
            InterestingEvents.X2_HANDOVER_REQUEST.value,  # 2058    
                
            # periodic events
            InterestingEvents.INTERNAL_PER_RADIO_UE_MEASUREMENT.value,  # 3075
            InterestingEvents.INTERNAL_PER_UE_RB_TRAFFIC_REP.value,  # 3077
            InterestingEvents.INTERNAL_PER_UE_TRAFFIC_REP.value,  # 3076
            
            # Other events known to InterestingEvents.Sanjib
            InterestingEvents.INTERNAL_EVENT_UE_CAPABILITY.value,  # 5172

            # ERAB events
            InterestingEvents.INTERNAL_EVENT_ERAB_DATA_INFO.value,  # 5202
            InterestingEvents.INTERNAL_PROC_ERAB_SETUP.value,       # 4099 
            InterestingEvents.INTERNAL_PROC_ERAB_RELEASE.value,     # 4114

            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION.value,   # 8
            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION_COMPLETE.value,  # 13
        ]
    
    @classmethod
    def isOpener(cls, value):
        """ Events that could open a session """         
        return value in [
            InterestingEvents.INTERNAL_PROC_RRC_CONN_SETUP.value, # 4097
            InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value,  # 4121
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value,  # 4103
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value,  # 4111
            ] 

    @classmethod
    def isStarter(cls, value):
        """ Events that could start a pattern """
        return value in [
            InterestingEvents.INTERNAL_PROC_INITIAL_CTXT_SETUP.value, # 4106 i2
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_IN.value,  # 4113
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_IN.value,  # 4105
            InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value,  # 4121
            ] 

    @classmethod
    def isEnder(cls, value):
        """ Events that could end session """ 
        return value in [             
            InterestingEvents.INTERNAL_PROC_HO_X2_EXEC_OUT.value,  # 4112
            InterestingEvents.INTERNAL_PROC_HO_S1_EXEC_OUT.value,  # 4104
            InterestingEvents.INTERNAL_PROC_UE_CTXT_RELEASE.value, # 4125
            ] 
            
    @classmethod
    def isCloser(cls, value):
        """ Events that could close a session if in error """ 
        return value in [ 
            InterestingEvents.INTERNAL_PROC_S1_SIG_CONN_SETUP.value, # 4098
            InterestingEvents.INTERNAL_PROC_RRC_CONN_SETUP.value, # 4097
            InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value, # 4121
            InterestingEvents.INTERNAL_PROC_INITIAL_CTXT_SETUP.value, # 4106 i3
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value,  # 4103
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value,  # 4111
            ] 

    @classmethod
    def isHo(cls, value):
        """ Events that could close a session if in error """ 
        return value in [ 
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_OUT.value,  # 4104
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_OUT.value,  # 4112
            InterestingEvents.INTERNAL_PROC_HO_EXEC_X2_IN.value,  # 4113
            InterestingEvents.INTERNAL_PROC_HO_EXEC_S1_IN.value,  # 4105
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_OUT.value,  # 4110
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_OUT.value,  # 4102
            InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value,  # 4111
            InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value,  # 4103
            ] 

    @classmethod
    def rcInfo(cls, value):
        """ get the info needed to process a resultcode 
        
        get name and position of result code and the none-error value
        """
        name = ''
        pos = -1
        noerror = -1
        if value == InterestingEvents.INTERNAL_PROC_S1_SIG_CONN_SETUP.value: # 4098
            name = 'EVENT_PARAM_S1_SIG_CONN_RESULT'  # todo use enum
            pos = 42
            noerror = '0'
        elif value == InterestingEvents.INTERNAL_PROC_RRC_CONN_SETUP.value:  # 4097
            name = 'EVENT_PARAM_RRC_RESULT'  # todo use enum
            pos = 49
            noerror = '0'
        elif value == InterestingEvents.INTERNAL_PROC_RRC_CONNECTION_RE_ESTABLISHMENT.value:  # 4121
            name = 'EVENT_PARAM_REESTAB_RESULT'  # todo use enum
            pos = 52
            noerror = '0'
        elif value == InterestingEvents.INTERNAL_PROC_INITIAL_CTXT_SETUP.value:  # 4106 i4
            name = 'EVENT_PARAM_INITIAL_CTXT_RESULT'  # todo use enum
            pos = 217
            noerror = '0'
        elif value == InterestingEvents.INTERNAL_PROC_HO_PREP_S1_IN.value:  # 4103
            name = 'EVENT_PARAM_PREP_IN_RESULT_UE_CTXT'  # todo use enum
            pos = 137
            noerror = '0'
        elif value == InterestingEvents.INTERNAL_PROC_HO_PREP_X2_IN.value:  # 4111
            name = 'EVENT_PARAM_PREP_IN_RESULT_UE_CTXT'  # todo use enum
            pos = 138
            noerror = '0'
        else:
            raise RuntimeError('Value %d is not a valid closer Event'%value)
        return pos, noerror, name   

    @classmethod
    def isExternal(cls, value):
        """ External Events that include ASN.1 msgs """ 
        return value in [             
            InterestingEvents.S1_INITIAL_UE_MESSAGE.value, # 1040
            InterestingEvents.S1_INITIAL_CONTEXT_SETUP_REQUEST.value,  # 1038
            InterestingEvents.S1_HANDOVER_REQUEST.value,  # 1034
            InterestingEvents.X2_HANDOVER_REQUEST.value,  # 2058
            InterestingEvents.X2_CONTEXT_RESPONSE.value,  # 2072
            InterestingEvents.S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE.value,  # 1045
            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION.value,   # 8
            InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION_COMPLETE.value,  # 13

            ] 

    @classmethod
    def getPadding(cls):
        """ get a random padding event to use """ 
        return random.choice([             
            InterestingEvents.INTERNAL_EVENT_UE_MOBILITY_EVAL,
            InterestingEvents.INTERNAL_EVENT_UE_CAPABILITY,
            InterestingEvents.INTERNAL_PER_RADIO_UE_MEASUREMENT,
            InterestingEvents.INTERNAL_PER_UE_RB_TRAFFIC_REP,
            InterestingEvents.INTERNAL_PER_UE_TRAFFIC_REP,
            ]) 


    @classmethod
    def asnInfo(cls, value):
        """ get the info needed to process an ASN.1 mesage
        
        get position of asn.1 message
        """
        pos = -1
        if value == InterestingEvents.X2_HANDOVER_REQUEST.value: # 2058
            pos = 42
        elif value == InterestingEvents.S1_INITIAL_UE_MESSAGE.value: # 1040
            pos = 42
        elif value == InterestingEvents.S1_INITIAL_CONTEXT_SETUP_REQUEST.value: # 1038
            pos = 42
        elif value == InterestingEvents.S1_HANDOVER_REQUEST.value: # 1034
            pos = 42
        elif value == InterestingEvents.X2_CONTEXT_FETCH_RESPONSE.value: # 2072
            pos = 42 #?
        elif value == InterestingEvents.S1_PATH_SWITCH_REQUEST_ACKNOWLEDGE.value: # 1045
            pos = 42
        elif value == InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION.value:   # 8
            pos = 42
        elif value == InterestingEvents.RRC_RRC_CONNECTION_RECONFIGURATION_COMPLETE.value:  # 13
            pos = 42
        else:
            raise RuntimeError('Value %d is not a valid External event!'%value)
        return pos
        


            
if __name__ == '__main__':
    assert True == InterestingEvents.has_value(4125)
    assert False == InterestingEvents.has_value(1234)
    
    assert False == InterestingEvents.isCloser(4125)
    assert False == InterestingEvents.isCloser(1234)
    assert True == InterestingEvents.isCloser(4106)
    
    assert True == InterestingEvents.isOpener(4121)
    assert False == InterestingEvents.isOpener(4122)
    
    assert 'EVENT_PARAM_REESTAB_RESULT' == InterestingEvents.rcInfo(4121)[2]
    
    for evt in InterestingEvents:
        InterestingEvents.isASRevt(evt)
        InterestingEvents.isASROnlyEvt(evt)
        InterestingEvents.isEBSLonlyEvt(evt)
        InterestingEvents.isCommonEvt(evt)
        if (InterestingEvents.isASROnlyEvt(evt.value) or
            InterestingEvents.isCommonEvt(evt.value) or 
            InterestingEvents.isEBSLonlyEvt(evt.value)):
            pass  # event is interesting 
        else:
            print('%s not an interesting event!'%evt) 
           
    evt = InterestingEvents.getPadding()  
    assert InterestingEvents.isASROnlyEvt(evt.value)

    print("# ASR Events ")
    for evt in InterestingEvents:
        #InterestingEvents.isASROnly(evt)
        #InterestingEvents.isASROnly(evt.value)
        if InterestingEvents.isASRevt(evt.value):
            print('"%s": %d,' %( evt.name, evt.value))
        
    print("# EBS-L Only ")
    for evt in InterestingEvents:
        #InterestingEvents.isASROnly(evt)
        #InterestingEvents.isASROnly(evt.value)
        if InterestingEvents.isEBSLonlyEvt(evt.value):
            print('"%s": %d,' %( evt.name, evt.value))

    print("# Common Only ")
    for evt in InterestingEvents:
        #InterestingEvents.isASROnly(evt)
        #InterestingEvents.isASROnly(evt.value)
        if InterestingEvents.isCommonEvt(evt.value):
            print('"%s": %d,' %( evt.name, evt.value))
        
    print("# ASR Only ")
    for evt in InterestingEvents:
        #InterestingEvents.isASROnly(evt)
        #InterestingEvents.isASROnly(evt.value)
        if InterestingEvents.isASROnlyEvt(evt.value):
            print('"%s": %d,' %( evt.name, evt.value))
        
    print('Done.')
