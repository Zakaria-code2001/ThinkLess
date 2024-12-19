# Tasks: Use Azure AD for Full User Management and Secure the Todo Service via API Management

## Introduction

In this continuation, we will enhance the Todo List application by fully utilizing Azure Active Directory (Azure AD) for user management, including authentication and storing user profiles. We will connect the Flask Azure Functions Todo service with the Azure AD authentication system using Azure API Management (API Gateway) to properly secure and expose the API endpoints.

**Goals:**

- Use Azure AD for both authentication and user profile management, eliminating the need for a separate user database.
- Modify the Flask Azure Functions Todo service to validate and accept Azure AD tokens.
- Configure Azure API Management to protect the APIs using Azure AD authentication.
- Ensure that only authenticated users can access and manipulate their own todo items.

---

## Table of Contents

1. Prerequisites
2. Set Up Azure Active Directory
3. Modify the Flask Azure Functions Todo Service
4. Secure the API with Azure API Management
5. Update the Frontend Application (Optional)
6. Test the Application
7. Security Considerations
8. Troubleshooting
9. Conclusion

---

## 1. Prerequisites

Ensure you have the following:

- **Existing Todo List Application**: Deployed on Azure using Flask, Azure Functions, Docker, and Azure PostgreSQL.
- **Azure Account**: With permissions to create Azure AD applications and API Management services.
- **Azure CLI**: Installed and logged in.
- **Python 3.9 or above**: Installed.
- **MSAL Library**: For Python, to handle Azure AD authentication.
- **(Optional) Frontend Application**: If you have a frontend, you'll update it to use Azure AD authentication.

---

## 2. Set Up Azure Active Directory

We'll use Azure AD to handle both authentication and user management.

### 2.1. Create an App Registration for the Backend (API)

1. **Navigate to Azure Active Directory**:
   - In the [Azure Portal](https://portal.azure.com/), go to **Azure Active Directory** > **App registrations**.

2. **Register a New Application**:
   - Click **New registration**.
   - **Name**: `TodoApi`.
   - **Supported account types**: Choose **Accounts in this organizational directory only** (appropriate for your scenario).
   - **Redirect URI**: Leave blank for the API.
   - Click **Register**.

3. **Expose an API**:
   - In the app registration for `TodoApi`, go to **Expose an API**.
   - Click **Set** next to **Application ID URI**, accept the default or customize it, and click **Save**.
   - **Add a Scope**:
     - Click **Add a scope**.
     - **Scope name**: `user_impersonation`
     - **Who can consent**: **Admins and users**
     - **Admin consent display name**: `Access Todo API`
     - **Admin consent description**: `Allows the app to access Todo API on behalf of the user.`
     - **State**: **Enabled**
     - Click **Add scope**.

### 2.2. Create an App Registration for the Frontend (Client)

1. **Register a New Application**:
   - Click **New registration**.
   - **Name**: `TodoAppClient`.
   - **Supported account types**: Same as above.
   - **Redirect URI**:
     - **Type**: Web (if using a web app) or Public client/native (if using SPA or mobile app).
     - **URI**: For development, use `http://localhost:3000` or appropriate.
   - Click **Register**.

2. **Configure API Permissions**:
   - In `TodoAppClient`, go to **API permissions**.
   - Click **Add a permission**.
   - Select **My APIs**.
   - Choose `TodoApi`.
   - Select the scope `user_impersonation`.
   - Click **Add permissions**.

3. **Grant Admin Consent**:
   - In **API permissions**, click **Grant admin consent for [Your Tenant Name]**.
   - Confirm the action.

4. **Authentication Settings**:
   - Go to **Authentication**.
   - Under **Redirect URIs**, ensure your application's redirect URI is listed.
   - Under **Implicit grant and hybrid flows**, if using a SPA, check **Access tokens** and **ID tokens**.

5. **Certificates & Secrets** (If using confidential client):
   - Go to **Certificates & secrets**, and create a new client secret.
   - Record the secret value.

### 2.3. Note the IDs

- **Application (client) ID** of both `TodoApi` and `TodoAppClient`.
- **Directory (tenant) ID**.

---

## 3. Modify the Flask Azure Functions Todo Service

Update your Flask API to require Azure AD authentication.

### 3.1. Install Required Libraries

Install `msal` and `pyjwt` libraries:

```bash
pip install msal pyjwt cryptography
```

### 3.2. Validate Access Tokens in the Flask API

Update your `app.py` to validate incoming access tokens.

#### Import Necessary Libraries

```python
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from functools import wraps
```

#### Configure Azure AD Settings

```python
TENANT_ID = '<your-tenant-id>'  # Directory (tenant) ID
CLIENT_ID = '<your-api-client-id>'  # Application ID of TodoApi
```

#### Implement Token Validation

Create a function to validate the access token:

```python
import json

class AzureADConfig:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.jwks_uri = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.algorithms = ["RS256"]

azure_ad_config = AzureADConfig(TENANT_ID)

def get_cached_public_keys():
    # You can implement caching here; for simplicity, fetch keys every time
    response = requests.get(azure_ad_config.jwks_uri)
    jwks = response.json()
    return jwks['keys']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            public_keys = get_cached_public_keys()
            decoded_token = None
            for key in public_keys:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                try:
                    decoded_token = jwt.decode(
                        token,
                        public_key,
                        algorithms=azure_ad_config.algorithms,
                        audience=CLIENT_ID,
                        issuer=azure_ad_config.issuer,
                    )
                    break
                except jwt.InvalidTokenError:
                    continue
            if not decoded_token:
                return jsonify({'message': 'Token is invalid!'}), 401
            # Extract user ID
            user_id = decoded_token.get('oid')
            if not user_id:
                return jsonify({'message': 'User ID not found in token.'}), 401
            request.user_id = user_id
        except Exception as e:
            return jsonify({'message': 'Token validation error.', 'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated
```

#### Protect API Endpoints

Apply the `@token_required` decorator to your endpoints:

```python
@app.route('/todos', methods=['GET'])
@token_required
def get_todos():
    user_id = request.user_id
    # Fetch todos for this user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, task FROM todos WHERE user_id = %s;', (user_id,))
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'id': todo[0], 'task': todo[1]} for todo in todos]), 200

@app.route('/todos', methods=['POST'])
@token_required
def add_todo():
    user_id = request.user_id
    task = request.json.get('task')
    if not task:
        return jsonify({'error': 'Task is required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todos (task, user_id) VALUES (%s, %s) RETURNING id;', (task, user_id))
    todo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': todo_id, 'task': task}), 201
```

#### Update Database Schema

Add a `user_id` column to the `todos` table:

```sql
ALTER TABLE todos ADD COLUMN user_id VARCHAR(255);
```

Or update your table creation script if starting fresh:

```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id SERIAL PRIMARY KEY,
        task TEXT NOT NULL,
        user_id VARCHAR(255) NOT NULL
    );
''')
```

---

## 4. Secure the API with Azure API Management

Use Azure API Management to expose your API securely, enforcing Azure AD authentication.

### 4.1. Create an API Management Service

1. **Create a New API Management Instance**:

   ```bash
   az apim create --resource-group $RESOURCE_GROUP --name <your-apim-name> --publisher-email <email> --publisher-name <name>
   ```

2. **Wait for the service to be provisioned**, as it can take some time.

### 4.2. Import Your Azure Function into API Management

1. **In the Azure Portal**, navigate to your API Management instance.

2. **Import the Function App**:

   - Go to **APIs** > **+ Add API** > **Function App**.
   - Select your Function App (the Flask Azure Function Todo service).
   - Import the functions you want to expose.

### 4.3. Configure Azure AD OAuth 2.0 Authentication

1. **Authorize the Developer Portal**:

   - In **Portal settings** of API Management, under **OAuth 2.0**, configure OAuth settings to allow developers to obtain tokens.

2. **Configure OAuth 2.0 Authorization Server in APIM**:

   - In APIM, go to **APIs** > **Authorization Servers** > **+ Add**.
     - **Name**: `azuread`
     - **Authorization endpoint URL**: `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize`
     - **Token endpoint URL**: `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token`
     - **Client ID**: Application ID of `TodoAppClient`
     - **Client Secret**: Client secret of `TodoAppClient` (if applicable)
     - **Scopes**: `api://{Your API Client ID}/user_impersonation`
     - **Grant types**: Check **Authorization code** and **Implicit** (if needed).
     - **Authorization methods**: Check **GET** and **POST**.

3. **Apply Validation Policies to the API**:

   - Go to your API, select an operation (e.g., `GET /todos`).
   - Click on **Policies**.
   - Add the following policy within the `<inbound>` section:

     ```xml
     <validate-jwt header-name="Authorization" failed-validation-httpcode="401" failed-validation-error-message="Unauthorized">
       <openid-config url="https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration" />
       <required-claims>
         <claim name="aud">
           <value>{Your API Client ID}</value>
         </claim>
       </required-claims>
     </validate-jwt>
     ```

   - Replace `{tenant_id}` and `{Your API Client ID}` with your actual values.

4. **Test the API**:

   - Use the APIM Developer Portal or tools like Postman to test the API.
   - Ensure that you obtain an access token from Azure AD and include it in the `Authorization` header.

---

## 5. Update the Frontend Application (Optional)

If you have a frontend application, update it to authenticate with Azure AD and consume the API via APIM.

### 5.1. Implement MSAL for Authentication

Use the Microsoft Authentication Library (MSAL) for your frontend.

#### Install MSAL

```bash
# For React applications
npm install @azure/msal-react @azure/msal-browser
```

#### Configure MSAL

```javascript
import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: "<Your Client App ID>", // From TodoAppClient
    authority: "https://login.microsoftonline.com/<Your Tenant ID>",
    redirectUri: "http://localhost:3000",
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
```

#### Acquire Token and Call API

```javascript
import { useMsal } from "@azure/msal-react";

const request = {
  scopes: ["api://<Your API Client ID>/user_impersonation"],
};

function CallApiExample() {
  const { instance, accounts } = useMsal();

  const callApi = async () => {
    const account = accounts[0];
    const response = await instance.acquireTokenSilent({
      ...request,
      account,
    });

    const accessToken = response.accessToken;

    const apiResponse = await fetch("https://<your-apim-name>.azure-api.net/todos", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    const data = await apiResponse.json();
    // Handle the data
  };

  return (
    <button onClick={callApi}>Call API</button>
  );
}
```

---

## 6. Test the Application

### 6.1. Test Authentication Flow

- Ensure that users can sign in via Azure AD.
- Verify that access tokens are obtained and used correctly.

### 6.2. Test API Access

- Attempt to access the API without an access token (should be denied).
- Access the API with a valid access token (should succeed).

### 6.3. Verify Data Access Control

- Ensure that users can only access their own todo items.
- Test creating, reading, updating, and deleting todos.

---

## 7. Security Considerations

- **Token Validation**: Always validate tokens on the server-side to authenticate and authorize requests.
- **Least Privilege**: Only request and grant the minimum necessary permissions (scopes).
- **Secure Storage**: Never expose client secrets in client-side code or source control.
- **HTTPS**: Use HTTPS for all communications to protect data in transit.
- **Cleanup and Revocation**: Implement mechanisms to handle user sign-out and token revocation if necessary.
- **Monitoring and Logging**: Use Azure Monitor and Application Insights to detect and respond to security incidents.

---

## 8. Troubleshooting

- **Access Denied Errors**: Ensure that the correct scopes are requested and granted.
- **Invalid Token Errors**: Verify that tokens are correctly obtained and included in API requests.
- **CORS Issues**: If using a frontend, configure CORS policies appropriately on the API.
- **Policy Misconfigurations**: Double-check APIM policies for correctness.

---

## 9. Conclusion

You have successfully enhanced your Todo List application to fully utilize Azure AD for user management and authentication. By integrating Azure API Management, you've secured your APIs and established a robust, scalable architecture that leverages Azure services effectively.

---

**Next Steps**:

- **Continuous Integration/Continuous Deployment (CI/CD)**: Automate your deployment processes.
- **Role-Based Access Control (RBAC)**: Implement more granular permissions if needed.
- **Scalability and Performance**: Monitor and optimize your application's performance.
- **Documentation**: Document your APIs for internal or external developers.

---

If you have any questions or need further assistance, feel free to ask!
