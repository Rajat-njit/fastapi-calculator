## 🚀 FastAPI Calculator — Full Backend Project (Auth + Polymorphic Calculations + CI/CD + Docker)

### **1. Overview**

This project implements a complete backend application using **FastAPI**, emphasizing **professional engineering practices**. Key features include secure user authentication, polymorphic calculation models, relational database persistence (PostgreSQL/SQLAlchemy), automated testing, and a full CI/CD pipeline with Docker integration.

The design focuses on: clean API structure, declarative SQLAlchemy models, Pydantic validation, token-based security, and an industry-style GitHub Actions pipeline.

#### **Core Features**

  * **User Management:** Registration and Login (JWT-based authentication).
  * **Calculations:** Full CRUD operations.
  * **Polymorphism:** Logic implemented via **subclasses** and the **Factory Pattern**.
  * **Database:** Relational persistence with automated DB migrations (`create_all`).
  * **Deployment:** Fully containerized using **Docker** & `docker-compose`.
  * **Testing:** Automated suite covering **Unit**, **Integration**, and **E2E** tests.

-----

### **2. Project Architecture**

The internal structure follows a professional, scalable FastAPI layout, promoting **high cohesion** and **low coupling**.

```
app/
 ├── api/
 │   ├── routes/          # All API routers (auth, calculations)
 │   └── dependencies/    # Authentication & DB dependencies
 ├── core/                # Security, settings, JWT, password hashing
 ├── models/              # SQLAlchemy ORM models (User, Calculation + subclasses)
 ├── schemas/             # Pydantic schemas for request/response validation
 ├── database.py          # Engine, SessionLocal, Base Config
 ├── main.py              # FastAPI app instance, router mounting, lifespan
tests/
 ├── unit/
 ├── integration/
 └── e2e/
```

#### **Design Rationale**

This structure ensures **testability** (clean dependency overrides), **scalability** (easy integration of new modules), and **professional readability**, aligning with industry expectations.

-----

### **3. Getting Started**

#### **3.1 Requirements**

Ensure the following dependencies are installed (as per `requirements.txt`):

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
pydantic
pydantic-settings
pytest
httpx
python-multipart
```

#### **3.2 Running Locally (Without Docker)**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your-username>/fastapi-calculator.git
    cd fastapi-calculator
    ```
2.  **Create virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

#### **3.3 Running with Docker**

For a quick deployment using the pre-built image:

```bash
docker pull <your-username>/fastapi-calculator:latest
docker run -p 8000:8000 <your-username>/fastapi-calculator
```

-----

### **4. Configuration & Environment**

#### **4.1 Environment Variables (`.env`)**

Application configuration is handled via environment variables, read by **Pydantic Settings** (in `app/core/config.py`). This is **critical for CI/CD** and containerization.

**Example `.env`:**

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
JWT_SECRET_KEY=super-secret-key
JWT_REFRESH_SECRET_KEY=super-refresh-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
```

#### **4.2 Application Settings (`app/core/config.py`)**

Configuration is completely decoupled from the source code, supporting `.env` files, GitHub Secrets, and Docker environment variables, ensuring industry-standard configuration management.

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    # ... other settings
```

-----

### **5. Database Layer Design**

The project uses **PostgreSQL** (with SQLAlchemy 2.0 Declarative Base) and employs key architectural decisions.

#### **5.1 UUID Primary Keys**

Both `User` and `Calculation` models use **UUID-based identifiers** (`String(36)` in Python, native UUID in Postgres). This prevents collisions and ensures predictability across environments.

#### **5.2 Polymorphic Calculation Table**

All calculation types (Addition, Subtraction, etc.) are stored in a **single table** using **SQLAlchemy Polymorphic Identity**.

  * Allows for easy filtering and consistent schema.
  * Enables child classes to override behavior (e.g., `get_result()`).

-----

### **6. Authentication & Security**

The application implements robust **JWT-based authentication**.

#### **6.1 Password Hashing**

Passwords are securely stored using **bcrypt** via the Passlib library.

```python
def get_password_hash(password: str):
    return pwd_context.hash(password)
```

#### **6.2 Token Creation & Validation**

Access tokens encode the **user ID (`sub`)** and include an **expiration time**. A FastAPI dependency reads the token, validates the signature and format, and fetches the authenticated user.

-----

### **7. Polymorphic Calculation Implementation**

This demonstrates advanced OOP and ORM usage, meeting the complexity requirements of the assignment.

#### **7.1 Factory Pattern**

Calculations are created via a single, flexible entry point that maps the calculation type string to the correct subclass:

```python
calc = Calculation.create("multiplication", user_id, inputs)

# Internally, the factory uses a mapping:
mapping = { "addition": Addition, "multiplication": Multiplication, ... }
```

#### **7.2 Overridden Behavior**

Each concrete calculation class implements its specific logic by overriding the core `get_result()` method.

```python
class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self):
        result = 1
        for v in self.inputs:
            result *= v
        return float(result)
```

This design is **extensible** and aligns perfectly with a flexible, testable model layer.

-----

### **8. API Endpoints**

#### **8.1 Authentication Endpoints**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/auth/register` | `POST` | Create a new user account. |
| `/auth/login` | `POST` | Authenticate and receive a JWT token. |

#### **8.2 Calculations Endpoints (Require Auth)**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/calculations` | `POST` | Create a new calculation (e.g., `{"type": "addition", "inputs": [1, 2]}`). |
| `/calculations` | `GET` | List all calculations created by the current user. |
| `/calculations/{id}` | `GET` | Retrieve a calculation by its UUID. |
| `/calculations/{id}` | `PUT` | Update calculation inputs and recompute the result. |
| `/calculations/{id}` | `DELETE` | Remove a calculation. |

-----

### **9. Testing Strategy (Unit, Integration, E2E)**

A thorough testing strategy is a major grading requirement and is implemented to verify correctness at every layer.

#### **9.1 Test Types**

  * **Unit Tests:** Test individual components (e.g., compute functions, factory mapping, schema validation).
  * **Integration Tests:** Test full DB interaction (CRUD operations) with a real SQLAlchemy session and token authentication.
  * **E2E Tests:** Simulate complete user flows (Register → Login → CRUD).

#### **9.2 Database Override (`conftest.py`)**

The `conftest.py` file is crucial for enabling isolated, reliable tests. It overrides the `get_db` dependency to ensure that:

  * Tests run against a clean, dedicated Postgres test instance (in CI) or SQLite (locally).
  * Tables are created and dropped per test session (`Base.metadata.create_all`/`drop_all`).

-----

### **10. CI/CD Pipeline (GitHub Actions & Docker)**

The automated pipeline reflects real-world engineering workflows.

#### **10.1 Pipeline Stages**

1.  **Setup:** Spin up a dedicated **Postgres 15** service.
2.  **Testing:** Install dependencies and run the complete **Unit, Integration, and E2E** test suite (`pytest`).
3.  **Security Scan:** Use **Trivy** to scan the Docker image for HIGH & CRITICAL CVEs.
4.  **Deployment:** Build the **Docker image** and push it to **Docker Hub**.

#### **10.2 Docker Deployment**

  * **Dockerfile:** Uses `python:3.11-slim`, non-root execution, and Uvicorn workers.
  * **`docker-compose.yml`:** Defines the multi-service local environment (`db: postgres:15`, `api: build .`).

The use of Docker ensures **reproducibility** and **environment consistency** from development to CI/CD.

-----

### **11. Security & Quality Checklist**

  * ✔ **Password hashing** (using **bcrypt**).
  * ✔ **JWT** with expiration for authentication.
  * ✔ **CORS** handling.
  * ✔ **DB-level cascading deletes** for data integrity.
  * ✔ Minimal data returned in API responses.

-----

### **12. Reflection Summary**

This project was a deep dive into modern backend construction. Implementing **polymorphism** and the **factory pattern** provided a flexible and scalable model layer. Secure **JWT authentication** reinforced dependency injection and security practices. Finally, building the **CI/CD pipeline**—integrating automated testing, Docker, and security scanning—provided invaluable hands-on experience with production-ready engineering workflows.

-----

### **13. Manual Testing Checklist**

All required manual steps have been verified:

1.  Register a new user.
2.  Log in and obtain a JWT token.
3.  Authorize the token in Swagger UI.
4.  `POST` to create a calculation.
5.  `GET` to list calculations.
6.  `GET` to retrieve by ID.
7.  `PUT` to update inputs and recompute the result.
8.  `DELETE` to remove the calculation.

---
