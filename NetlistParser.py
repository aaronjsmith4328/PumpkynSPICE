from PySpice.Spice.Parser import SpiceParser

class NetlistParser():

    def __init__(self, net_file_name: str) -> None:
        self.net_file_name = net_file_name
        self.parser = self._parse_netlist(file_name = net_file_name)
        self.circuit = self._build_circuit(self.parser)

    def _parse_netlist(self, file_name: str) -> SpiceParser:
        return SpiceParser(source=open(file_name).read())

    def _build_circuit(self, parser: 'SpiceParser'):
        return parser.build_circuit()
