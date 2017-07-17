from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import BoardInfo, InfoType, ULRange, FunctionType
from mcculw.examples.props.propsbase import Props
from mcculw.ul import ULError


class AnalogOutputProps(Props):
    """Provides analog output information on the hardware configured at the
    board number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num

        self.resolution = self._get_resolution()
        self.num_chans = self._get_num_chans()
        self.available_ranges = self._get_available_ranges()
        self.supports_v_out = self._get_supports_v_out(
            self.available_ranges)
        self.supports_scan = self._get_supports_scan()

    def _get_resolution(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.DACRES)

    def _get_num_chans(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.NUMDACHANS)

    def _get_supports_scan(self):
        try:
            ul.get_status(self._board_num, FunctionType.AOFUNCTION)
        except ULError:
            return False
        return True

    def _get_available_ranges(self):
        result = []

        # Check if the range is ignored by passing a bogus range in
        try:
            ul.a_out(self._board_num, 0, -5, 0)
            range_ignored = True
        except ULError:
            range_ignored = False

        if range_ignored:
            # Try and get the range configured in InstaCal
            try:
                curr_range = ULRange(ul.get_config(
                    InfoType.BOARDINFO, self._board_num, 0,
                    BoardInfo.DACRANGE))
                result.append(curr_range)
            except ULError:
                pass
            return result

        for dac_range in ULRange:
            try:
                ul.a_out(self._board_num, 0, dac_range, 0)
                result.append(dac_range)
            except ULError:
                pass

        return result

    def _get_supports_v_out(self, available_ranges):
        if len(available_ranges) == 0:
            return False
        try:
            ul.v_out(self._board_num, 0, available_ranges[0], 0)
        except ULError:
            return False
        return True