"""Automatically generate passive income apps docker-compose file."""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from pathlib import Path

import yaml
from pydantic import BaseModel


class Emulator(BaseModel):
    """Emulator that enables the containers to run on Raspberry pi."""

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "tonistiigi/binfmt",
            "privileged": True,
            "command": "--install 'x86_64'",
        }


class Honeygain(BaseModel):
    """Honeygain provider including the YAML for the corresponding docker-compose set-up."""

    email: str
    password: str

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "honeygain/honeygain",
            "platform": "linux/amd64",
            "command": f"-tou-accept -email {self.email} -pass {self.password} -device {str(uuid.uuid4())}",
            "restart": "on-failure",
            "depends_on": {
                Emulator().__class__.__name__: {
                    "condition": "service_completed_successfully"
                }
            },
        }


class Peer2Profit(BaseModel):
    """Peer2Profit provider including the YAML for the corresponding docker-compose set-up."""

    email: str

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "peer2profit/peer2profit_linux",
            "restart": "on-failure",
            "network_mode": "host",
            "environment": {"P2P_EMAIL": f"{self.email}"},
            "depends_on": {
                Emulator().__class__.__name__: {
                    "condition": "service_completed_successfully"
                }
            },
        }


class Iproyal(BaseModel):
    """Iproyal provider including the YAML for the corresponding docker-compose set-up."""

    email: str
    password: str

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "iproyal/pawns-cli",
            "command": f"-email={self.email} -password={self.password} -device-name=raspberrypi -accept-tos",
            "restart": "on-failure",
            "depends_on": {
                Emulator().__class__.__name__: {
                    "condition": "service_completed_successfully"
                }
            },
        }


class Packetstream(BaseModel):
    """Packetstream provider including the YAML for the corresponding docker-compose set-up."""

    CID: str

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "packetstream/psclient",
            "platform": "linux/amd64",
            "restart": "on-failure",
            "environment": {"CID": f"{self.CID}"},
            "depends_on": {
                Emulator().__class__.__name__: {
                    "condition": "service_completed_successfully"
                }
            },
        }


class Earnapp(BaseModel):
    """Earnapp provider including the YAML for the corresponding docker-compose set-up."""

    UUID: str

    @property
    def yaml(self):
        """The docker-compose entry."""
        return {
            "container_name": f"{self.__class__.__name__}",
            "image": "fazalfarhan01/earnapp:lite",
            "environment": {"EARNAPP_UUID": f"{self.UUID}"},
            "restart": "on-failure",
            "depends_on": {
                Emulator().__class__.__name__: {
                    "condition": "service_completed_successfully"
                }
            },
        }


@dataclass
class InstallService:
    """Request the desired passive income apps to be installed and create docker-compose file."""

    initialized_services: list = field(default_factory=lambda: [], init=False)

    class Providers(Enum):
        """Available providers that can be incorporated."""
        HONEYGAIN = "Honeygain"
        PEER2PROFIT = "Peer2Profit"
        IPROYAL = "IProyal"
        PACKETSTREAM = "Packetstream"
        EARNAPP = "Earnapp"

    def __post_init__(self):
        self._initialize_provider_details()

    def _request_provider_installs(self) -> List[str]:
        """Loop through full list of providers and return providers that need to be installed."""
        install_list = [k.value for k in self.Providers]
        AFFIRMATIVE_RESPONSE = ("y", "yes")
        NEGATIVE_RESPONSE = ("n", "no")

        for provider in install_list.copy():
            while True:
                try:
                    install_provider = input(
                        f"Would you like to install {provider}?. Answer 'y' or 'n'.\n"
                    )
                    if install_provider.lower() in NEGATIVE_RESPONSE+AFFIRMATIVE_RESPONSE:
                        if install_provider.lower() in NEGATIVE_RESPONSE:
                            install_list.remove(provider)
                        break
                except Exception:
                    print("Answer 'y' or 'n'")
        return install_list

    def _initialize_provider_details(self):
        """Initialize required providers."""
        install_list = self._request_provider_installs()

        for provider in install_list:
            if provider == self.Providers.HONEYGAIN.value:
                email = input(f"Please provide {provider} email.\n")
                password = input(f"Please provide {provider} password.\n")
                self.initialized_services.append(
                    Honeygain(email=email, password=password)
                )

            if provider == self.Providers.PEER2PROFIT.value:
                email = input(f"Please provide {provider} email.\n")
                self.initialized_services.append(Peer2Profit(email=email))

            if provider == self.Providers.IPROYAL.value:
                email = input(f"Please provide {provider} email.\n")
                password = input(f"Please provide {provider} password.\n")
                self.initialized_services.append(
                    Iproyal(email=email, password=password)
                )

            if provider == self.Providers.PACKETSTREAM.value:
                CID = input(f"Please provide {provider} CID.\n")
                self.initialized_services.append(Packetstream(CID=CID))

            if provider == self.Providers.EARNAPP.value:
                UUID = input(f"Please provide {provider} UUID.\n")
                self.initialized_services.append(Earnapp(UUID=UUID))

    def prepare_docker_compose(self) -> dict:
        """Create the complete dict that will transform into the YAML."""
        if not self.initialized_services:
            raise ValueError("No YAML will be created.")

        self.initialized_services.insert(0, Emulator())
        return {
            "version": "3",
            "services": {
                s.__class__.__name__: s.yaml for s in self.initialized_services
            },
        }


if __name__ == "__main__":
    install_service = InstallService()

    with open(Path(__file__).parent.parent / "output" / "docker-compose.yml", "w") as outfile:
        yaml.dump(
            install_service.prepare_docker_compose(),
            outfile,
            default_flow_style=False,
            sort_keys=False,
        )
    print(
        "A full docker-compose YAML for the requested providers has been generated and is ready for use!"
    )
