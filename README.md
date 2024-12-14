# **ExchTracker: Insights from Crypto Exchanges**

ExchTracker is a Python-based data pipeline that leverages the CoinGecko API to extract, analyze, and export insights about cryptocurrency exchanges and markets. The pipeline processes data, performs analysis, and exports results locally or to an S3 bucket. This project is designed to be robust, extensible, and easy to configure for various use cases.

---

## **Features**
- **Fetch Data**: Retrieve market and exchange data from CoinGecko.
- **Analyze Data**:
  - Identify exchanges with similar trading pairs.
  - Generate historical trading volumes for shared markets.
  - Analyze trade volume trends for similar exchanges.
- **Export Results**:
  - Save analyzed data locally as CSV files.
  - Optionally upload files to S3 for storage or further processing.
- **Configuration**:
  - Flexible configuration through command-line arguments or JSON config files.
- **Retry Mechanism**:
  - Handles throttling and transient errors with exponential backoff.

---

## **Project Structure**
```
src/
├── adapters/                 # Adapters for external APIs (e.g., S3, Bitso, CoinGecko)
├── config/                   # Configuration classes and utilities
├── constants/                # Application constants
├── core/                     # Core pipeline and analysis logic
├── di/                       # Dependency injection container
├── utils/                    # Utility classes and functions
tests/                        # Unit tests for all modules
```

---

## **Requirements**
- Python 3.9+
- Docker & Docker Compose
- AWS CLI (optional for interacting with S3 directly)

---

## **Setup**

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd exchtracker
```

### 2. **Install Python Dependencies**
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. **Run Docker Containers**
Start the LocalStack (S3) and Python app containers:
```bash
make up
```

### 4. **Run Tests**
To ensure everything is working, run the tests:
```bash
make tests
```

---

## **Usage**

### **Running the Pipeline Locally**
Run the main script with default settings:
```bash
make run-local
```

### **Running the Pipeline in Docker**
```bash
make run-docker
```

### **Custom Configuration**

#### **Using Command-Line Arguments**
```bash
python src/main.py \
    --rate_limiter_max_retries 5 \
    --exchanges_with_similar_trades_to_analyze 10 \
    --exchanges_to_analyze_limit 20 \
    --historical_data_lookback_days 30 \
    --log_level DEBUG \
    --write_to_s3
```

#### **Using a Config File**
Create a JSON configuration file:
```json
{
    "rate_limiter_max_retries": 5,
    "historical_data_lookback_days": 30,
    "log_level": "DEBUG",
    "exchanges_with_similar_trades_to_analyze": 10,
    "exchanges_to_analyze_limit": 20,
    "write_to_s3": true
}
```

Run the pipeline with the config file:
```bash
python src/main.py --config path/to/config.json
```

---

## **Environment Variables**
The project uses the following environment variables:

| Variable              | Description                                | Default Value       |
|-----------------------|--------------------------------------------|---------------------|
| `AWS_ACCESS_KEY_ID`   | AWS access key for LocalStack              | `test`              |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for LocalStack             | `test`              |
| `AWS_REGION`          | AWS region for LocalStack                 | `us-east-1`         |
| `S3_ENDPOINT`         | S3 endpoint for LocalStack                | `http://localstack:4566` |
| `AWS_BUCKET`          | S3 bucket name                            | `exchtracker`       |

---

## **Makefile Commands**

| Command       | Description                                     |
|---------------|-------------------------------------------------|
| `make build`  | Build Docker containers                        |
| `make up`     | Start Docker containers                        |
| `make down`   | Stop and remove Docker containers              |
| `make logs`   | View logs from Docker containers               |
| `make tests`  | Run all unit tests                             |
| `make run-local` | Run the pipeline locally                     |
| `make run-docker` | Run the pipeline in the Docker container    |
| `make clean`  | Remove all Docker containers and volumes       |

---

## **Tests**
The project includes comprehensive unit tests for all modules. Run the tests locally:
```bash
make tests
```

---

## **Design Highlights**
- **Dependency Injection**: Centralized dependency management via a DI container.
- **Retry Mechanism**: Robust handling of API rate limits and transient failures with exponential backoff.
- **Local and S3 Support**: Flexible output options for analyzed data.
- **Modular Structure**: Extensible design for adding new data sources or analysis steps.

---

## **License**
This project is licensed under the MIT License.

---

## **Contact**
For any issues or suggestions, please reach out to [your-email@example.com].

---

This `README.md` provides clear instructions for setup, usage, and understanding the project's design and functionality, making it developer-friendly and professional.