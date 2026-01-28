FROM python:3.12-slim as pym2base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    cmake \
    git \
    libfreetype6 \
    libgomp1 \
    libstdc++6 \
    libglu1-mesa-dev \
    libtiff5-dev \
    qtbase5-dev \
    qtscript5-dev \
    libqt5svg5-dev \
    libqt5opengl5-dev \
    libqt5xmlpatterns5-dev \
    qtwebengine5-dev \
    qttools5-dev \
    libqt5charts5-dev \
    libqt5x11extras5-dev \
    qtxmlpatterns5-dev-tools \
    libqt5webengine-data \
    libopenslide-dev \
    && rm -rf /var/lib/apt/lists/*


FROM pym2base
# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the conversion script
COPY imzml_to_nrrd.py .

# Create input and output directories
RUN mkdir -p /input /output

# Set environment variable for unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Set the entrypoint to the script
ENTRYPOINT ["python", "imzml_to_nrrd.py"]

# Default arguments (can be overridden)
CMD ["--help"]
