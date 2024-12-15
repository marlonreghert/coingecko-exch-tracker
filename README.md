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
  - Upload files to S3 for storage or further processing (can be disabled)
- **Configuration**:
  - Flexible configuration through command-line arguments or JSON config files.
- **Retry Mechanism**:
  - Handles throttling and transient errors with exponential backoff.

---

## **Requirements**
- Python 3.9+
- Docker & Docker Compose
- Docker Daemon running (required for LocalStack)
- AWS CLI (optional for interacting with S3 directly)

---

## **Setup**

### **1. Running with Docker Compose**

Start the application and its dependencies (LocalStack) using Docker Compose:
```bash
make build
make up
```

To view logs:
```bash
make logs
```

To stop and clean up containers:
```bash
make down
```

### **2. Accessing the LocalStack Web App**
LocalStack provides a web UI for exploring the S3 service and inspecting files. After starting the containers, open your browser and navigate to:
```
http://localhost:4566/_localstack
```

From here, you can inspect and manage the S3 folders and files.

### **3. Running the Application Locally**

#### **Install Dependencies**
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

#### **Run the Pipeline**
Run the pipeline locally with default configurations:
```bash
make run-local
```

#### **Run Tests**
Run all unit tests locally:
```bash
make tests
```

---

## **Usage**

### **Command-Line Arguments**
You can configure the pipeline directly using command-line arguments:
```bash
python src/main.py \
    --rate_limiter_max_retries 5 \
    --exchanges_with_similar_trades_to_analyze 10 \
    --exchanges_to_analyze_limit 20 \
    --historical_data_lookback_days 30 \
    --log_level DEBUG \
    --write_to_s3
```

### **Using a Config File**
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

The following environment variables are used for the Docker-based setup:

| Variable              | Description                                | Default Value       |
|-----------------------|--------------------------------------------|---------------------|
| `AWS_ACCESS_KEY_ID`   | AWS access key for LocalStack              | `test`              |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for LocalStack             | `test`              |
| `AWS_REGION`          | AWS region for LocalStack                 | `us-east-1`         |
| `S3_ENDPOINT`         | S3 endpoint for LocalStack                | `http://localstack:4566` |
| `AWS_BUCKET`          | S3 bucket name                            | `exchtracker`       |

---

## **Makefile Commands**

| Command           | Description                                     |
|-------------------|-------------------------------------------------|
| `make build`      | Build Docker containers                        |
| `make up`         | Start Docker containers                        |
| `make down`       | Stop and remove Docker containers              |
| `make logs`       | View logs from Docker containers               |
| `make tests`      | Run all unit tests                             |
| `make run-local`  | Run the pipeline locally                       |
| `make run-docker` | Run the pipeline in the Docker container        |
| `make clean`      | Remove all Docker containers and volumes       |

---

## **Tests**

Run all unit tests:
```bash
make tests
```

Test coverage includes:
- Core pipeline logic
- Retry mechanisms
- Analysis and export functions
- Integration with LocalStack for S3 functionality

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

For any issues or suggestions, please reach out to [marlonreghert@gmail.com].

---
