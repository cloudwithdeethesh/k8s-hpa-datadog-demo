# Use full Python image for better debugging capabilities
FROM python:3.9

# Install system utilities and debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    iputils-ping \
    telnet \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY calculator.py .
COPY templates/ templates/

# Expose port 8000
EXPOSE 8000

# Run the application with ddtrace-run
CMD ["ddtrace-run", "python", "calculator.py"]