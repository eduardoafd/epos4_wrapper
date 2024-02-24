from ctypes import *


class Motor:
    def __init__(self, node_id=0, dll_path='./epos_cmd_lib/EposCmd64.dll'):
        super(Motor, self).__init__()

        cdll.LoadLibrary(dll_path)
        self._epos = CDLL(dll_path)

        self._node_id = node_id
        self._position = c_long()
        self._error_code = c_uint()

        self._keyHandle = None

    def connect(self):
        self._keyHandle = self._epos.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', b'USB0',
                                                    byref(self._error_code))

    def disconnect(self):
        self.set_enable_state(False)
        self._epos.VCS_CloseDevice(self._keyHandle, byref(self._error_code))

    def set_enable_state(self, enable=True):
        if enable:
            self._epos.VCS_SetEnableState(self._keyHandle, self._node_id, byref(self._error_code))
        else:
            self._epos.VCS_SetDisableState(self._keyHandle, self._node_id, byref(self._error_code))

    def clear_faults(self):
        # When faults are cleared the position is zeroed
        self._epos.VCS_ClearFault(self._keyHandle, self._node_id, byref(self._error_code))

    def get_position(self):
        if self._keyHandle:
            ret = self._epos.VCS_GetPositionIs(self._keyHandle, self._node_id, byref(self._position),
                                               byref(self._error_code))

            if ret:
                return self._position.value
            else:
                return None
        else:
            raise SystemExit

    def set_control_mode(self, control_mode, enable=False):
        if control_mode == 0:
            self._epos.VCS_ActivateProfilePositionMode(self._keyHandle, self._node_id, byref(self._error_code))
        elif control_mode == 1:
            self._epos.VCS_ActivateProfileVelocityMode(self._keyHandle, self._node_id, byref(self._error_code))
        elif control_mode == 2:
            self._epos.VCS_ActivateCurrentMode(self._keyHandle, self._node_id, byref(self._error_code))

        if enable:
            self.set_enable_state(True)

    def set_position(self, position: int, absolute=True):
        self._epos.VCS_MoveToPosition(self._keyHandle, self._node_id, c_long(position), absolute, 0,
                                      byref(self._error_code))

    def set_current(self, current: int):
        self._epos.VCS_SetCurrentMust(self._keyHandle, self._node_id, c_short(current), byref(self._error_code))
