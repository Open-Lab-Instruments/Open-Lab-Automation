# Open Lab Automation

Open Lab Automation is an open-source software suite for automated electrical measurements, designed for hobbyists, makers, and lab enthusiasts. It features a modern Python (PyQt5) graphical user interface (GUI) for instrument configuration and control, and a C backend for fast, low-level communication with laboratory instruments via USB, LAN, GPIB, or serial interfaces.

**Note: This software is currently under active development. Features and stability may change, and some functionalities may be incomplete or experimental.**

## Features

- **Instrument Management:**
  - Add, configure, and manage instruments using a flexible JSON-based instrument library.
  - Three-level selection: instrument type → series → model, with dynamic options based on the library.
  - Support for power supplies, dataloggers, oscilloscopes, and electronic loads.
  - Assign connection parameters and channels/slots for each instrument.
  - Compose VISA addresses with a guided dialog for each interface type (LXI, GPIB, USB, RS232, etc.).
  - All UI elements are fully translatable (Italian, English, French, Spanish, German).

- **Project Management:**
  - Create and manage measurement projects with associated configuration files (.json, .inst, .eff, .was).
  - Advanced naming options for files and instances.
  - Edit instrument, efficiency, and oscilloscope settings with dedicated dialogs.

- **Backend Communication:**
  - C backend for efficient, low-level communication with instruments.
  - Designed to be easily extended for new instrument types and protocols.

## Structure

- **Frontend:** Python (PyQt5)
- **Backend:** C
- **Instrument Library:** JSON (see `Instruments_LIB/instruments_lib.json`)

## Requirements

- Python 3.7+
- PyQt5
- GCC (for backend compilation)

## Disclaimer

**This software is provided for hobbyist and non-professional use only.**

The authors and contributors of Open Lab Automation do not take any responsibility for damages to equipment, property, or persons resulting from the use of this software. Use it at your own risk. The software is provided "as is" without warranty of any kind, express or implied. It is not intended for use in professional, industrial, or safety-critical environments.

## License

See the LICENSE file for details.
