# **Exchange Tracker**

Exchange Tracker is a tool designed to monitor and analyze market activities across various cryptocurrency exchanges, providing insights into market trends, trustworthiness, and competitive trading volumes. The tool is built to assist the Assets Team in making strategic decisions based on up-to-date data.

---

## **Features**
- Fetches detailed cryptocurrency exchange data using the Coingecko API.
- Provides daily updated tables:
  - **Exchanges Table**: Key details of exchanges with markets similar to Bitso.
  - **Shared Markets Table**: Links exchanges with markets shared with Bitso.
  - **Historical Volume Table**: Rolling 30-day trading volumes for shared markets.
  - **Rolling Volume Table for Exchanges (BTC)**: Rolling 30-day BTC trading volumes.
- Automated updates to ensure data freshness.

---

## **Setup and Usage**

### **1. Local Setup**
#### **Run Tests**
```bash
make test
```

#### **Run Application**
```bash
make run
```

---

### **2. Docker Workflow**
#### **Build Docker Image**
```bash
make docker-build
```

#### **Run Docker Container**
```bash
make docker-run
```

#### **Access the Docker Container**
To inspect or interact with the container:
```bash
make docker-shell
```

#### **View Processed Data**
To list files in the `/data/processed` folder inside the container:
```bash
make view-processed
```

#### **Stop and Remove Docker Container**
```bash
make docker-clean
```

---

## **Project Structure**
```plaintext
├── src/
│   └── table_updater.py    # Main application logic
├── tests/
│   └── test_*.py           # Unit tests
├── data/                   # Data storage directory (shared with Docker)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build file
├── Makefile                # Automation scripts
└── README.md               # Project documentation
```

---

## **Technical Requirements**
- **Python 3.10+**
- **Docker** installed for containerized deployment
- Dependencies listed in `requirements.txt`

---

## **How It Works**
1. Fetches exchange and market data from Coingecko.
2. Processes the data into structured tables:
   - Exchange details
   - Shared market relationships
   - Historical and rolling trading volumes
3. Automatically updates tables daily for consistent and accurate insights.

---

## **Contributing**
Feel free to open issues or submit pull requests to improve the tool.

---

## **License**
This project is licensed under the [MIT License](LICENSE).