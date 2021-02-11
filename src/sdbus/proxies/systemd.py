# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from __future__ import annotations

from typing import Any, Generator, List, Optional, Tuple, Literal

from .._proxies_common import (SystemdActiveState, SystemdUnitListTuple,
                               SystemdUnitStartModes, SystemdUnitStopModes)
from ..dbus_proxy_sync import DbusInterfaceCommon, dbus_method, dbus_property
from ..sd_bus_internals import SdBus, encode_object_path


class SystemdManager(
        DbusInterfaceCommon,
        interface_name='org.freedesktop.systemd1.Manager'):

    def __init__(self, bus: Optional[SdBus] = None):
        super().__init__('org.freedesktop.systemd1',
                         '/org/freedesktop/systemd1',
                         bus)

    @dbus_method()
    def list_units(self) -> List[
            Tuple[str, str, str, str, str, str, str, int, str, str]]:

        raise NotImplementedError

    def list_units_named(self
                         ) -> Generator[SystemdUnitListTuple, None, None]:
        for x in self.list_units():
            yield SystemdUnitListTuple(*x)

    @dbus_method()
    def subscribe(self) -> None:
        raise NotImplementedError

    @dbus_method()
    def unsubscribe(self) -> None:
        raise NotImplementedError

    @dbus_property()
    def version(self) -> str:
        raise NotImplementedError


class SystemdUnit(
        DbusInterfaceCommon,
        interface_name='org.freedesktop.systemd1.Unit'):

    def __init__(self, unit_name: str, bus: Optional[SdBus] = None):
        super().__init__('org.freedesktop.systemd1',
                         encode_object_path(
                             '/org/freedesktop/systemd1/unit', unit_name),
                         bus)

    @dbus_method()
    def freeze(self) -> None:
        raise NotImplementedError

    @dbus_method()
    def thaw(self) -> None:
        raise NotImplementedError

    @dbus_method('si')
    def kill(
            self,
            kill_who: Literal['main', 'controll', 'all'],
            signal: int,) -> None:
        raise NotImplementedError

    @dbus_method('s')
    def reload(
            self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method('s')
    def reload_or_restart(
            self, mode: SystemdUnitStartModes) -> str:

        raise NotImplementedError

    @dbus_method('s')
    def reload_or_try_restart(
            self, mode: SystemdUnitStartModes) -> str:

        raise NotImplementedError

    @dbus_method()
    def reset_failed(self) -> None:
        raise NotImplementedError

    @dbus_method('s')
    def restart(
            self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method('ba(sv)')
    def set_properties(
            self,
            is_runtime: bool,
            properties: List[Tuple[str, Tuple[str, Any]]]) -> None:
        raise NotImplementedError

    @dbus_method('s')
    def start(self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_method('s')
    def stop(self, mode: SystemdUnitStopModes) -> str:
        raise NotImplementedError

    @dbus_method('s')
    def try_restart(self, mode: SystemdUnitStartModes) -> str:
        raise NotImplementedError

    @dbus_property()
    def active_state(self) -> SystemdActiveState:
        raise NotImplementedError

    @dbus_property()
    def sub_state(self) -> str:
        raise NotImplementedError


__all__ = ('SystemdManager', 'SystemdUnitListTuple', 'SystemdUnit')
