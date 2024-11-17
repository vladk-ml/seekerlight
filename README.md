# SeekerLight

A web-based satellite imagery analysis platform for exploring and visualizing SAR (Synthetic Aperture Radar) data using Google Earth Engine.

## Features

- Interactive SAR data visualization
- VH/VV polarization selection
- Orbit pass filtering (Ascending/Descending)
- Custom Area of Interest (AOI) management
- Temporal analysis capabilities
- User-friendly web interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/seekerlight.git
cd seekerlight
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Earth Engine:
- You need a Google Earth Engine account
- Run `earthengine authenticate` to set up authentication

## Usage

1. Start the application:
```bash
python run.py
```

2. Open your web browser to the URL shown in the terminal (usually http://localhost:8866)

3. Use the interface to:
   - Select or draw Areas of Interest
   - Choose polarization (VH/VV)
   - Set date range for analysis
   - Filter by orbit pass
   - Export results

## Requirements

- Python 3.9+
- Google Earth Engine account
- Modern web browser

## License

MIT License - See LICENSE file for details
