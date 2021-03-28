import os

from core import Functions
from core.util.BasicUtil import log
from core.util.KNXDUtil import DPTXlatorFactoryFacade
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorValueError


class KNXGateway:
    """ central singleton instance with KNX Gateway host information """
    __instance = None
    __hostIP = None

    def __new__(cls, *args, **kwargs):
        if KNXGateway.__instance is None:
            KNXGateway.__instance = object.__new__(cls)
        return KNXGateway.__instance

    def setHostIP(self, hostIP):
        KNXGateway.__hostIP = hostIP

    @property
    def hostIP(self):
        """ IP address of the machine where KNXD process is running """
        return KNXGateway.__hostIP


class KNXDDevice:
    """ allows the interaction with the KNX representation via KNXD Gateway """

    #########################################
    #   KNX specific methods, read/write    #
    #########################################
    def readKNXAttribute(self):
        """ reads values via the KNXD command line tool """
        # TODO implementation
        pass

    def writeKNXAttribute(self, attrName, knxDest, knxFormat, val, function=None) -> bool:
        """
        writes values via the KNXD command line tool
        :returns true if successful
        """
        dpt = None

        # get DPT implementation
        dc = DPTXlatorFactoryFacade().create(knxFormat)

        # perform transformations if defined before sending to bus
        if function:
            val = self.performFunction(dc.dpt, function, val)

        # convert to DPT representation
        try:
            if dc.checkValue(val):
                dpt = dc.valueToData(val)
        except DPTXlatorValueError:
            # log failure
            log('error',
                f'Value could not be updated "{attrName}"[{knxDest}] value={val} - Check type definition for DPT type "{knxFormat}" and value "{val}"')
        except (TypeError, ValueError) as ex:
            # log failure
            log('error',
                f'Value could not be updated "{attrName}"[{knxDest}] value={val} - {ex}')

        if not dpt:
            return False

        # do not load the bus with unnecessary request, check against cached value
        if not self.isCurrentKNXAttribute(knxDest, knxFormat, dpt):
            # send value to the knx bus
            os.popen('knxtool groupwrite ip:{0} {1} {2}'.format(KNXGateway().hostIP,
                                                                knxDest,
                                                                dpt))
            # log success
            log('change',
                f'Updated value on KNX bus "{attrName}"[{knxDest}] value={val}[DPT:{dpt}]')
        else:
            # log success
            log('info',
                f'Value is up to date "{attrName}"[{knxDest}] value={val}')

        return True

    def performFunction(self, dpt, function, val):
        """ calls Functions library, overwrite in case of client specific behavior required """
        return Functions.executeFunction(dpt, function, val)

    def isCurrentKNXAttribute(self, knxDest, knxFormat, newVal) -> bool:
        """
        checks whether new value matches to stored value last sent on the bus
        :param knxFormat:   DPT format that is expected for the given destination
        :param knxDest:     KNX destionation under which the value is stored
        :param newVal:      value in dpt representation
        :returns            true if new value matches cached value
        """
        curKNXVal = os.popen("knxtool groupcacheread ip:{0} {1} | "
                             "while read a b c data; do echo $data; done"
                             .format(KNXGateway().hostIP, knxDest)).read()[:-1]

        # special cases
        if curKNXVal == '00':
            curKNXVal = '0'
        elif curKNXVal == '01':
            curKNXVal = '1'

        return curKNXVal == newVal

    #########################################
    #   custom client methods, read/write   #
    #########################################
    def getAttribute(self, name, format, attr):
        """ retrieves the value from specific client and converts it into python datatype"""
        raise NotImplementedError

    # TODO define format for setAttribute abstract methods
