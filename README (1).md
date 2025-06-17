# Online Shopping Microservices System

A modular e-commerce platform based on Microservices architecture using .NET 7 and RabbitMQ for asynchronous communication.

---

## Requirements

1. **Operating System:** Windows 64-bit
2. **RabbitMQ Service:**  
   - Install locally **OR** run via **Docker Desktop**
3. **.NET Runtime:** [.NET 7.0](https://dotnet.microsoft.com/en-us/download/dotnet/7.0) must be installed

---

## Folder Structure

```
OnlineShoppingSystem
├── For Win-64                  # Executable services (compiled for Windows 64-bit)
├── Source Code                 # Microservices source code
├── README.txt                  # Setup instructions (this file in original format)
├── Report (DOCX & PDF)         # Project report files
```

---

## Run Instructions

### 1. Start RabbitMQ

- **Via Docker (recommended):**
  ```bash
  docker run -d rabbitmq
  ```

- **Locally (if installed):**
  ```cmd
  net start RabbitMQ
  ```

> Ensure RabbitMQ path is added to the system environment variables if running locally.

---

### 2. Start the Services

Go to the `For Win-64` folder and **run these executables in order** (double-click each):

1. `UsersService.exe`
2. `ProductsService.exe`
3. `ProductsService2.exe`
4. `OrdersService.exe`
5. `PaymentsService.exe`
6. `ApiGateway.exe`

---

## API Usage

Use tools like **Postman** or **Thunder Client** to send requests to the services via the **API Gateway**:  
`http://localhost:7000/gateway/`

> All requests **must** include the header:
```http
x-api-key: <your_api_key>
```

### API Keys by Role

| Role   | Key    | Permissions               |
|--------|--------|---------------------------|
| Admin  | 99999  | Full access               |
| User   | 12345  | Limited access            |
| Guest  | 00000  | Create account & view only|

---

## Services and Endpoints

### 1. **User Management**
- **Endpoint:** `/users`
- **Methods:**
  - `GET` – List users *(Admin/User)*
  - `POST` – Register new user *(Guest/Admin)*
  - `DELETE` – Delete user *(Admin)*
  - `PUT` – Update user info *(Admin)*

---

### 2. **Product Management**
- **Endpoint:** `/products`
- **Methods:**
  - `GET` – View products *(All roles)*
  - `DELETE` – Delete product *(Admin)*
  - `PUT` – Update product *(Admin)*

---

### 3. **Order Management**
- **Endpoint:** `/orders`
- **Methods:**
  - `GET` – List orders *(Admin/User)*
  - `POST` – Create order *(Admin/User)*
  - `DELETE` – Delete order *(Admin)*
  - `PUT` – Update order *(Admin)*

---

### 4. **Payment Management**
- **Endpoint:** `/payments`
- **Methods:**
  - `GET` – View payments *(Admin/User)*
  - `DELETE` – Delete payment *(Admin)*
  - `PUT` – Update payment *(Admin)*

---

## Notes & Tips

- **RabbitMQ** is required for all service communication via publish-subscribe model.
- Requests without a valid `x-api-key` will receive a `401 Unauthorized` response.
- **All requests go through the API Gateway** – no need to access internal services directly.
- When creating an order (`POST /orders`), a log will appear in `PaymentsService` showing asynchronous message handling.
- Admins can view **all users**, while standard users can only view **their own info**.
- Repeated requests to `/products` may return different categories (e.g., electronics, perfumes) due to load balancing between `ProductsService` and `ProductsService2`.

---

> Developed by Reem (321116), Sarah (326852), and Elias (335295) – MWS_WDC_HW1_F24
