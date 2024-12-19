# Tasks

### 0. Setting Up Your Azure Account

**Mandatory**

In this task, you will set up your Azure account to get started with the project.

**Steps:**

- **Sign Up or Sign In to Azure:**

  Visit the [Azure Portal](https://portal.azure.com/) and sign in with your Microsoft account. If you don't have an account, sign up for a free trial.

- **Install Azure CLI:**

  ```bash
  # On macOS
  brew update && brew install azure-cli

  # Log in to Azure
  az login
  ```

---

### 1. Creating an Azure PostgreSQL Database

**Mandatory**

In this task, you will create an Azure PostgreSQL server that will be used by your Todo List application.

**Steps:**

1. **Define Variables and Create a Resource Group:**

   ```bash
   # Define variables
   RESOURCE_GROUP=<your-resource-group-name>
   LOCATION=<your-location> # e.g., eastus
   POSTGRES_SERVER=<your-unique-server-name> # must be globally unique
   POSTGRES_ADMIN_USER=<admin-username>
   POSTGRES_ADMIN_PASSWORD=<secure-password>
   POSTGRES_DB=todo_db

   # Create the resource group
   az group create --name $RESOURCE_GROUP --location $LOCATION
   ```

2. **Create the Flexible PostgreSQL Server:**

   ```bash
   az postgres flexible-server create \
     --resource-group $RESOURCE_GROUP \
     --name $POSTGRES_SERVER \
     --admin-user $POSTGRES_ADMIN_USER \
     --admin-password $POSTGRES_ADMIN_PASSWORD \
     --database-name $POSTGRES_DB \
     --location $LOCATION \
     --public-access 0.0.0.0
   ```

3. **Configure Firewall Rules:**

   Allow access from Azure services:

   ```bash
   az postgres flexible-server firewall-rule create \
     --resource-group $RESOURCE_GROUP \
     --name $POSTGRES_SERVER \
     --rule-name AllowAllAzureIPs \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

---

### 2. Creating the Flask Application

**Mandatory**

In this task, you will develop a simple Flask application to handle your Todo List REST API.

**Steps:**

1. **Set Up the Development Environment:**

   ```bash
   # Create a directory for the application
   mkdir todo_app
   cd todo_app

   # Create a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**

   Create a `requirements.txt` file with the following content:

   ```txt
   flask
   psycopg2-binary
   azure-functions
   gunicorn
   ```

   Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Create Application Files:**

   - **app.py**

     ```python
     from flask import Flask, request, jsonify
     import os
     import psycopg2

     app = Flask(__name__)

     # Database configuration
     DB_HOST = os.getenv('DB_HOST')
     DB_NAME = os.getenv('DB_NAME')
     DB_USER = os.getenv('DB_USER')
     DB_PASSWORD = os.getenv('DB_PASSWORD')
     DB_PORT = os.getenv('DB_PORT', '5432')

     def get_db_connection():
         conn = psycopg2.connect(
             host=DB_HOST,
             database=DB_NAME,
             user=DB_USER,
             password=DB_PASSWORD,
             port=DB_PORT
         )
         return conn

     @app.route('/todos', methods=['GET'])
     def get_todos():
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute('SELECT id, task FROM todos;')
         todos = cursor.fetchall()
         cursor.close()
         conn.close()
         return jsonify([{'id': todo[0], 'task': todo[1]} for todo in todos]), 200

     @app.route('/todos', methods=['POST'])
     def add_todo():
         task = request.json.get('task')
         if not task:
             return jsonify({'error': 'Task is required'}), 400
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute('INSERT INTO todos (task) VALUES (%s) RETURNING id;', (task,))
         todo_id = cursor.fetchone()[0]
         conn.commit()
         cursor.close()
         conn.close()
         return jsonify({'id': todo_id, 'task': task}), 201

     @app.route('/todos/<int:todo_id>', methods=['PUT'])
     def update_todo(todo_id):
         task = request.json.get('task')
         if not task:
             return jsonify({'error': 'Task is required'}), 400
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute('UPDATE todos SET task = %s WHERE id = %s;', (task, todo_id))
         conn.commit()
         cursor.close()
         conn.close()
         return jsonify({'id': todo_id, 'task': task}), 200

     @app.route('/todos/<int:todo_id>', methods=['DELETE'])
     def delete_todo(todo_id):
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute('DELETE FROM todos WHERE id = %s;', (todo_id,))
         conn.commit()
         cursor.close()
         conn.close()
         return '', 204

     if __name__ == '__main__':
         app.run(host='0.0.0.0', port=80)
     ```

   - **init_db.py**

     ```python
     import psycopg2
     import os

     # Database configuration
     DB_HOST = os.getenv('DB_HOST')
     DB_NAME = os.getenv('DB_NAME')
     DB_USER = os.getenv('DB_USER')
     DB_PASSWORD = os.getenv('DB_PASSWORD')
     DB_PORT = os.getenv('DB_PORT', '5432')

     conn = psycopg2.connect(
         host=DB_HOST,
         database=DB_NAME,
         user=DB_USER,
         password=DB_PASSWORD,
         port=DB_PORT
     )
     cursor = conn.cursor()
     cursor.execute('''
         CREATE TABLE IF NOT EXISTS todos (
             id SERIAL PRIMARY KEY,
             task TEXT NOT NULL
         );
     ''')
     conn.commit()
     cursor.close()
     conn.close()
     print("Database initialized.")
     ```

4. **Initialize the Database:**

   Set the environment variables and run the script:

   ```bash
   export DB_HOST=<your-postgres-server>.postgres.database.azure.com
   export DB_NAME=$POSTGRES_DB
   export DB_USER=$POSTGRES_ADMIN_USER@$POSTGRES_SERVER
   export DB_PASSWORD=$POSTGRES_ADMIN_PASSWORD

   python init_db.py
   ```

---

### 3. Dockerize the Flask Application

**Mandatory**

In this task, you will create a Docker image of your Flask application to facilitate deployment.

**Steps:**

1. **Create the Dockerfile:**

   ```dockerfile
   FROM python:3.9-slim

   ENV PYTHONUNBUFFERED=1

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 80

   CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
   ```

2. **Create the .dockerignore File:**

   ```
   venv
   __pycache__
   *.pyc
   .env
   ```

---

### 4. Integrate Flask with Azure Functions

**Mandatory**

In this task, you will integrate your Flask application with Azure Functions to benefit from a serverless architecture.

**Steps:**

1. **Initialize the Azure Functions Project:**

   ```bash
   func init . --docker --python
   ```

2. **Create an HTTP Trigger Function:**

   ```bash
   func new --name FlaskFunction --template "HTTP trigger" --authlevel "anonymous"
   ```

3. **Modify the Function to Use Flask:**

   - **FlaskFunction/__init__.py**

     ```python
     import azure.functions as func
     from flask import Flask, request, jsonify
     from azure.functions import WsgiMiddleware
     import os
     import psycopg2

     # Import the Flask app
     from app import app as flask_app

     def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
         return WsgiMiddleware(flask_app).handle(req, context)
     ```

---

### 5. Build and Test the Docker Image Locally

**Mandatory**

In this task, you will build the Docker image and test the application on your local environment.

**Steps:**

1. **Build the Docker Image:**

   ```bash
   docker build -t todo-app .
   ```

2. **Run the Docker Container:**

   ```bash
   docker run -p 8080:80 \
     -e DB_HOST=<your-postgres-server>.postgres.database.azure.com \
     -e DB_NAME=$POSTGRES_DB \
     -e DB_USER=$POSTGRES_ADMIN_USER@$POSTGRES_SERVER \
     -e DB_PASSWORD=$POSTGRES_ADMIN_PASSWORD \
     todo-app
   ```

3. **Test the API Endpoints:**

   - Get all todos:

     ```bash
     curl http://localhost:8080/todos
     ```

   - Add a new todo:

     ```bash
     curl -X POST http://localhost:8080/todos \
       -H "Content-Type: application/json" \
       -d '{"task": "Buy milk"}'
     ```

---

### 6. Push the Docker Image to Azure Container Registry

**Mandatory**

In this task, you will upload your Docker image to Azure Container Registry (ACR) to prepare it for deployment.

**Steps:**

1. **Create an Azure Container Registry:**

   ```bash
   ACR_NAME=<your-unique-acr-name>

   az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
   ```

2. **Login to Your ACR:**

   ```bash
   az acr login --name $ACR_NAME
   ```

3. **Tag and Push the Image:**

   ```bash
   docker tag todo-app $ACR_NAME.azurecr.io/todo-app
   docker push $ACR_NAME.azurecr.io/todo-app
   ```

---

### 7. Deploy to Azure Functions

**Mandatory**

In this task, you will deploy your application to Azure Functions using the Docker image.

**Steps:**

1. **Create a Storage Account:**

   ```bash
   STORAGE_ACCOUNT_NAME=<your-storage-account-name>

   az storage account create \
     --resource-group $RESOURCE_GROUP \
     --name $STORAGE_ACCOUNT_NAME \
     --location $LOCATION \
     --sku Standard_LRS
   ```

2. **Create the Function App:**

   ```bash
   FUNCTION_APP_NAME=<your-unique-function-app-name>

   az functionapp create \
     --resource-group $RESOURCE_GROUP \
     --os-type Linux \
     --consumption-plan-location $LOCATION \
     --name $FUNCTION_APP_NAME \
     --storage-account $STORAGE_ACCOUNT_NAME \
     --runtime python \
     --functions-version 4 \
     --deployment-container-image-name $ACR_NAME.azurecr.io/todo-app
   ```

3. **Configure the Function App to Use the Docker Image:**

   ```bash
   az functionapp config container set \
     --name $FUNCTION_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --docker-custom-image-name $ACR_NAME.azurecr.io/todo-app \
     --docker-registry-server-url https://$ACR_NAME.azurecr.io
   ```

---

### 8. Configure Environment Variables on Azure

**Mandatory**

In this task, you will set up the necessary environment variables for database connection.

**Steps:**

1. **Configure Application Settings:**

   ```bash
   az functionapp config appsettings set \
     --name $FUNCTION_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --settings \
     DB_HOST=$POSTGRES_SERVER.postgres.database.azure.com \
     DB_NAME=$POSTGRES_DB \
     DB_USER=$POSTGRES_ADMIN_USER@$POSTGRES_SERVER \
     DB_PASSWORD=$POSTGRES_ADMIN_PASSWORD \
     DB_PORT=5432
   ```

---

### 9. Test the Deployed Application

**Mandatory**

In this task, you will verify that your application works correctly once deployed to Azure.

**Steps:**

1. **Retrieve the Function App URL:**

   ```bash
   FUNCTION_APP_URL=$(az functionapp show \
     --name $FUNCTION_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --query defaultHostName -o tsv)

   echo "Function App URL: https://$FUNCTION_APP_URL"
   ```

2. **Test the API Endpoints:**

   - Get all todos:

     ```bash
     curl https://$FUNCTION_APP_URL/todos
     ```

   - Add a new todo:

     ```bash
     curl -X POST https://$FUNCTION_APP_URL/todos \
       -H "Content-Type: application/json" \
       -d '{"task": "Walk the dog"}'
     ```

---

### 10. (Optional) Configure Azure API Management

**Optional**

If you wish to manage multiple services through an API Gateway, you can configure Azure API Management.

**Steps:**

- **Create an Azure API Management Instance:**

  ```bash
  az apim create --resource-group $RESOURCE_GROUP --name <api-management-name> --publisher-email <email> --publisher-name <name>
  ```

- **Import Your Function App Endpoints:**

  In the Azure portal, go to your API Management instance and add your Function App as an API.

---

### 11. (Optional) Create a Frontend Application

**Optional**

To interact with your API, you can develop a frontend application using frameworks like React.

**Steps:**

1. **Create a React App:**

   ```bash
   npx create-react-app todo-frontend
   cd todo-frontend
   ```

2. **Set the API Endpoint in Your Application:**

   Edit the `.env` file:

   ```env
   REACT_APP_API_URL=https://$FUNCTION_APP_URL
   ```

3. **Implement Functionality to Interact with the API:**

   Use fetch or axios to make requests to the `/todos` endpoints.

---

### 12. Security Best Practices

**Mandatory**

- **Protect Credentials:** Use Azure Key Vault to store sensitive information.

- **Limit Database Access:** Properly configure firewall rules.

- **Use HTTPS:** Ensure all communications are encrypted.

- **Implement Authentication:** Consider using Azure AD or other authentication methods.

- **Monitor the Application:** Use Azure Monitor and Application Insights for monitoring.

---

### 13. Troubleshooting

**Mandatory**

- **Function Fails to Start:** Check logs with `az functionapp log tail`.

- **Database Connection Issues:** Verify environment variables and firewall rules.

- **Docker Image Not Found:** Ensure you have pushed the image to the correct ACR.

- **General Errors:** Consult Azure documentation or search for solutions specific to the error encountered.

---

### 14. Conclusion

You have successfully set up and deployed your Todo List REST API using Flask, Azure Functions, Docker, and Azure PostgreSQL. This architecture provides scalability and flexibility to further expand your application.

---

**Repo:**

- **GitHub Repository:** [your-repository-name]
- **Directory:** `todo_app`
- **Files:**
  - `app.py`
  - `init_db.py`
  - `requirements.txt`
  - `Dockerfile`
  - `FlaskFunction/__init__.py`

---

**Tips:**

- Replace all placeholders (`<...>`) with your specific values.

- Keep your source code updated using a version control system like Git.

- Consider implementing CI/CD pipelines to automate the build and deployment process.

---

If you need further assistance or have any questions, feel free to ask!
